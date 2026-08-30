"""Dựng LangGraph cho feature ``photo-sort`` — một **vòng reconcile**, không phải
pipeline biến đổi tuần tự.

Ý tưởng: *chẩn đoán trước, chỉ sửa đúng chỗ sai, rồi kiểm lại tới khi hội tụ* —
giống control-loop của Kubernetes / autofix của linter. ``check`` liệt kê vi phạm
SOP của đầu vào; mỗi fixer **tự bỏ qua** khi không có vi phạm thuộc loại nó xử lý;
``validate`` kiểm lại và lặp với ``agent_repair`` (LLM) cho phần còn sót.

**MỘT luồng duy nhất** — graph luôn có đủ node, không dựng khác nhau theo config.
Config chỉ tinh chỉnh *hành vi bên trong* node (vd ``vision_assist``, ``prefer_images``,
``max_repair_iters``), không đổi *hình dạng* graph.

Sơ đồ
=====
::

    START
      │
      ▼
    scan ─────────── đọc trạm → ctx.data:
      │                photos[] · assign={folder hiện tại: [ảnh]} · hm_dirs · meta
      ▼
    check ────────── LIỆT KÊ mọi vi phạm SOP của ĐẦU VÀO THÔ → ctx.data["issues"]
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
    agent_repair ───────────┘   ReAct agent (agent_core) sửa ctx.data["assign"] bằng
      │  soft=True                tool; chỉ mutate in-memory. Tự bỏ qua nếu hết issue /
      │                           không có LLM_API_KEY. Bounded ``max_repair_iters``.
      │
      │ hết issue / hết vòng
      ▼
    plan ─────────── assign → danh sách Move (di chuyển + đổi tên + PNG→JPG)
      ▼
    verify ───────── HARD: mọi ảnh xuất hiện đúng 1 lần, không trùng (folder, tên).
      │                aborted → END ngay, KHÔNG apply.
      ▼
    apply ────────── thực thi Move (safe_move: không đè, journal → resume được).
      │                dry-run → bỏ qua.
      ▼
    delete_empty ─── xoá thư mục rỗng ngoài kế hoạch. dry-run → bỏ qua.
      ▼
     END

Bất biến thiết kế
================
1. ``check`` là hàm THUẦN — chỉ đọc ``assign``, không mutate, không rẽ nhánh.
2. Mỗi fixer nằm trên chain tuyến tính → chạy **đúng 1 lần**, và tự bỏ qua khi
   không có issue thuộc loại nó xử lý ⇒ vòng lặp LUÔN dừng.
3. ``dot_range`` / ``scaffold`` / ``even_four`` re-derive điều kiện từ ``assign``
   HIỆN TẠI (không tin ``ctx.data["issues"]`` của ``check`` vì state đổi sau classify).
4. Invariant CỨNG (bảo toàn ảnh) là node ``verify`` RIÊNG, chạy sau mọi fixer,
   không bao giờ giao cho fixer.
5. Deterministic trước (classify … even_four), LLM (``agent_repair``) sau cùng + có cap.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from graphrun import GraphState

from photo_sort import steps

#: số vòng validate ↔ agent_repair tối đa (chốt chặn, không phải tuỳ biến)
_MAX_REPAIR_ITERS = 3

#: chain reconcile, chạy đúng thứ tự này; mỗi node tự bỏ qua khi không có việc
_CHAIN = ["scan", "check", "classify", "vision", "dot_range", "scaffold", "even_four"]

#: node graph -> step function
_NODES = {
    "scan": steps.scan,
    "check": steps.check,
    "classify": steps.classify,
    "vision": steps.vision,
    "dot_range": steps.dot_range,
    "scaffold": steps.scaffold,
    "even_four": steps.even_four,
    "validate": steps.validate,
    "agent_repair": steps.agent_repair,
    "plan": steps.plan,
    "verify": steps.conservation,
    "apply": steps.apply,
    "delete_empty": steps.delete_empty,
}


def build_graph(config) -> StateGraph:
    """Lắp vòng reconcile. Graph LUÔN giống nhau — xem docstring module cho sơ đồ.

    ``config`` chỉ mang DỮ LIỆU (rules, naming, dot_range, keep_as_is, prefer_images…),
    không có cờ bật/tắt node.
    """
    g = StateGraph(GraphState)
    for name, fn in _NODES.items():
        g.add_node(name, fn)

    g.add_edge(START, _CHAIN[0])
    for a, b in zip(_CHAIN, _CHAIN[1:]):
        g.add_edge(a, b)

    # ── validate ↔ agent_repair loop (bounded) ─────────────────────────
    g.add_edge(_CHAIN[-1], "validate")
    g.add_edge("agent_repair", "validate")

    def repair_gate(state) -> str:
        d = state["ctx"].data
        exhausted = not d.get("issues") or d.get("repair_iters", 0) >= _MAX_REPAIR_ITERS
        return "plan" if exhausted else "agent_repair"

    g.add_conditional_edges("validate", repair_gate,
                            {"plan": "plan", "agent_repair": "agent_repair"})

    # ── plan → verify → apply → delete_empty ───────────────────────────
    g.add_edge("plan", "verify")
    g.add_conditional_edges(
        "verify",
        lambda s: END if s["ctx"].report.aborted else "apply",
        {"apply": "apply", END: END},
    )
    g.add_edge("apply", "delete_empty")
    g.add_edge("delete_empty", END)
    return g
