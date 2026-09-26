"""Dựng LangGraph cho feature ``photo-sort`` — một **vòng reconcile**, không phải
pipeline biến đổi tuần tự.

Ý tưởng: *chẩn đoán trước, chỉ sửa đúng chỗ sai, rồi kiểm lại tới khi hội tụ* —
giống control-loop của Kubernetes / autofix của linter. ``check`` liệt kê vi phạm
SOP của đầu vào; mỗi fixer **tự bỏ qua** khi không có vi phạm thuộc loại nó xử lý;
``validate`` kiểm lại và lặp với ``agent_repair`` (LLM) cho phần còn sót.

**MỘT luồng duy nhất** — graph LUÔN có đủ 15 node (kể cả ``vision`` và ``agent_repair``),
KHÔNG có cờ bật/tắt. Config chỉ mang DỮ LIỆU (rules, naming, prefer_images…), không đổi
hình dạng graph. AI (``vision`` / ``agent_repair``) cần ``.env`` với ``LLM_API_KEY``
(bắt buộc — xem :mod:`llm.config`); thiếu thì node soft-skip, pipeline vẫn chạy.

Sơ đồ
=====
::

    START
      │
      ▼
    scan ─────────── đọc trạm → ctx.data:
      │                photos[] · assign={folder hiện tại: [ảnh]} · hm_dirs · meta
      ▼
    check ────────── LIỆT KÊ mọi vi phạm SOP của ĐẦU VÀO THÔ → state(ctx).issues
      │                + report["vấn đề đầu vào"]. Hàm THUẦN: không sửa, không rẽ nhánh.
      ▼
    classify ─────── fixer cho  unclassified / misplaced  (rule-match: mỗi ảnh → 1
      │                thư mục đích). Tự bỏ qua nếu đầu vào đã đúng chỗ.
      ▼
    vision ───────── LLM vét ảnh chưa xếp / nghi bản vẽ (có cache). Tự bỏ qua nếu
      │                không có LLM_API_KEY / không có ảnh cần xem.
      ▼
    dot_range ─────── fixer Mục 2: gộp thư mục per-đốt → 2 cực trị. Tự bỏ qua nếu
      │                không có block ``[[dot_range]]`` / không có thư mục per-đốt.
      ▼
    canonicalize ─── đổi tên thư mục con về tên CHUẨN ``[[subfolders]]`` (gộp trùng,
      │                dựng ``ensure``); không khớp → "cần người xem". Bỏ qua nếu không khai.
      ▼
    scaffold ─────── fixer cho  too_few / odd_folders / missing_khac  — mỗi hạng
      │                mục ≥2 thư mục "Công tác" (cặp) + 1 "Hình ảnh khác".
      ▼
    even_four ─────── fixer cho  odd_images / too_many  — ép số ảnh chẵn, ≤ prefer_images.
      │
      ▼
    validate ◄──────────────┐   kiểm lại (CHỈ invariant cấu trúc, tính tươi mỗi vòng)
      │                     │
      │ còn issue &         │
      │ vòng < max ─────────┤
      ▼                     │
    agent_repair ───────────┘   ReAct agent (llm) sửa state(ctx).assign bằng tool;
      │  soft=True                chỉ mutate in-memory. Lượt đầu còn RÀ SOÁT ảnh ở 'khác'
      │                           (tool look = vision theo hạng mục, [agent] trong rules).
      │                           Tự bỏ qua nếu không có việc / không có LLM_API_KEY.
      │
      │ hết issue / hết vòng
      ▼
    plan ─────────── assign → danh sách Move (di chuyển + đổi tên + PNG→JPG)
      ▼
    verify ───────── HARD: mọi ảnh xuất hiện đúng 1 lần, không trùng (folder, tên).
      │                fail → ctx.report.abort() → apply/delete_empty tự no-op (@node).
      ▼
    apply ────────── thực thi Move (safe_move: không đè, journal → resume được).
      │                aborted → bỏ qua.
      ▼
    delete_empty ─── xoá thư mục rỗng ngoài kế hoạch.
      ▼
     END

Bất biến thiết kế
================
1. ``check`` là hàm THUẦN — chỉ đọc ``assign``, không mutate, không rẽ nhánh.
2. Mỗi fixer nằm trên chain tuyến tính → chạy **đúng 1 lần**, và tự bỏ qua khi
   không có issue thuộc loại nó xử lý ⇒ vòng lặp LUÔN dừng.
3. ``dot_range`` / ``scaffold`` / ``even_four`` re-derive điều kiện từ ``assign``
   HIỆN TẠI (không tin ``state(ctx).issues`` của ``check`` vì state đổi sau classify).
4. Invariant CỨNG (bảo toàn ảnh) là node ``verify`` RIÊNG, chạy sau mọi fixer,
   không bao giờ giao cho fixer.
5. Deterministic trước (classify … even_four), LLM (``agent_repair``) sau cùng + có cap.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from domain.profile import Profile
from runtime import GraphState

import steps
from domain.state import state

#: số vòng validate ↔ agent_repair tối đa (chốt chặn, không phải tuỳ biến)
_MAX_REPAIR_ITERS = 3

#: chain reconcile, chạy đúng thứ tự này; mỗi node tự bỏ qua khi không có việc
_CHAIN = ["scan", "normalize", "check", "classify", "vision", "dot_range", "canonicalize",
          "scaffold", "even_four"]

#: node graph -> step function
_NODES = {
    "scan": steps.scan,
    "normalize": steps.normalize,
    "check": steps.check,
    "classify": steps.classify,
    "vision": steps.vision,
    "dot_range": steps.dot_range,
    "canonicalize": steps.canonicalize,
    "scaffold": steps.scaffold,
    "even_four": steps.even_four,
    "validate": steps.validate,
    "agent_repair": steps.agent_repair,
    "plan": steps.plan,
    "verify": steps.conservation,
    "apply": steps.apply,
    "delete_empty": steps.delete_empty,
}


#: đồ thị chỉ là 2 đoạn thẳng nối bằng vòng lặp validate ↔ agent_repair.
#: @node tự bỏ qua khi không có việc / khi ctx.report.aborted → không cần rẽ nhánh khác.
_HEAD = [START, *_CHAIN, "validate"]                          # scan … even_four → validate
_TAIL = ["plan", "verify", "apply", "delete_empty", END]      # plan → … → END


def build_graph(config=None) -> StateGraph:
    """Lắp vòng reconcile. Graph LUÔN giống nhau, KHÔNG có cờ bật/tắt — xem docstring module.

    ``config`` không dùng ở đây (chỉ mang DỮ LIỆU, đã nạp qua Config trước khi tới node).
    """
    g = StateGraph(GraphState)
    for name, fn in _NODES.items():
        g.add_node(name, fn)
    for seg in (_HEAD, _TAIL):
        for a, b in zip(seg, seg[1:]):
            g.add_edge(a, b)

    # vòng lặp: agent_repair quay lại validate; validate lặp tiếp nếu CÒN issue &
    # chưa hết _MAX_REPAIR_ITERS vòng, ngược lại đi thẳng plan.
    g.add_edge("agent_repair", "validate")

    def loop_or_plan(graph_state) -> str:
        ctx = graph_state["ctx"]
        s = state(ctx)
        # lượt đầu còn việc RÀ SOÁT ảnh ('khác') dù cấu trúc đã hợp lệ → vẫn gọi agent 1 lần
        review = Profile.of(ctx).agent.get("review", False) and not s.reviewed
        done = (not s.issues and not review) or s.repair_iters >= _MAX_REPAIR_ITERS
        return "plan" if done else "agent_repair"

    g.add_conditional_edges("validate", loop_or_plan,
                            {"plan": "plan", "agent_repair": "agent_repair"})
    return g
