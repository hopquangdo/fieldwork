# Hướng phát triển thêm cho 3 package (`packages/`)

Rà soát: `agent-core`, `filesystem-tools`, `graphrun`.

## 1. `agent-core` (runtime agent)

| Hạng mục | Gợi ý thêm |
|---|---|
| Quan sát/streaming | `Agent` mới chỉ có `run`/`stream`. Thêm callback `on_tool_start/on_tool_end`, đếm token, log usage/cost mỗi lượt. Hỗ trợ `astream`/`arun` (async) — LangGraph có sẵn. |
| Kiểm soát vòng lặp | Thêm `max_iterations` / `recursion_limit` param (hiện phải truyền qua `config` thủ công), xử lý khi chạm giới hạn (trả về lý do rõ ràng thay vì raise). |
| Bền vững | Retry/backoff khi lỗi mạng/429, timeout mỗi lời gọi model, fallback model (primary → secondary). |
| Bộ nhớ hội thoại | Có `checkpointer` nhưng chưa có helper. Thêm `Agent.thread(id)` để quản lý history, cắt/summarize context khi dài. |
| Human-in-the-loop | `interrupt_before` cho các tool "nguy hiểm" (move/mkdir), yêu cầu duyệt trước khi thực thi. |
| ToolExecutor | Hiện tuần tự. Thêm: chạy song song các call độc lập, biến `${step1.output}` tham chiếu kết quả bước trước, dùng chung `emit()`/journal như graphrun để audit. |
| Structured output | Helper `agent.run(..., response_format=PydanticModel)` để lấy kết quả có schema. |
| Model factory | Cache instance model; validate sớm khi thiếu API key; hỗ trợ thêm `LLM_EXTRA_HEADERS`, `max_tokens`, `thinking` (Anthropic). |

## 2. `filesystem-tools`

| Hạng mục | Gợi ý thêm |
|---|---|
| Trùng lặp code | `fs_tools/agent/tools.py` tự cài `_within` trong khi `fs_tools.core` đã có `resolve_within`/`SandboxError`. README mô tả 6 tool theo module (`scan/read/view/move/rename/mkdir`) nhưng `agent/tools.py` chỉ có 5 và không theo cấu trúc module-per-tool như README → cần đồng bộ lại. |
| Tool còn thiếu | `stat` (metadata 1 file), `find`/`glob` (lọc theo pattern/size/ngày), `read` theo offset/dòng cho file lớn, `head`/`tail`. |
| Ghi có kiểm soát | Hiện "không bao giờ ghi/xóa". Thêm `write`/`append`/`delete` tùy chọn qua flag (`make_fs_tools(root, allow_write=True)`), giữ mặc định an toàn. |
| `view` | Hỗ trợ PDF (render trang), nhiều ảnh 1 lần, giới hạn tổng payload để tránh vượt context. |
| Undo/nhật ký | Ghi journal các thao tác move/rename để hoàn tác (khớp concept journal của graphrun). |
| Bất đồng bộ / hiệu năng | `walk_files` async, giới hạn độ sâu, bỏ qua theo `.gitignore`/pattern. |
| Community sunset | Như README ghi chú — cân nhắc bỏ hẳn `langchain-community`, tự implement 6 backend (đa số đã custom rồi). |

## 3. `graphrun`

| Hạng mục | Gợi ý thêm |
|---|---|
| Resume thực thi | README nói có `--resume` + journal, nhưng `runner.run` chạy graph từ đầu; cần tích hợp LangGraph checkpointer để resume đúng ở node dang dở, không chỉ replay journal. |
| Chạy song song / concurrency | Giới hạn số job đồng thời trong API (`jobs.py`), hàng đợi, hủy job (`DELETE /jobs/{id}`). |
| Bền vững job | Job hiện in-memory (last 50). Lưu xuống đĩa/SQLite để sống sót qua restart server. |
| Observability | Xuất OpenTelemetry/metrics, thời lượng mỗi stage, token/chi phí per run; endpoint `/jobs/{id}/report.html`. |
| Retry node | `@node(retries=2, backoff=...)` cho node mạng; hiện chỉ có `soft=True` (skip). |
| Bảo mật API | Có `GRAPHRUN_ALLOWED_ROOTS` + 403; thêm auth token, rate limit, cấu hình CORS. |
| CLI | `graphrun show <feature>` (in spec + default rules), `graphrun validate <rules.toml>`, `--watch` tái chạy khi input đổi. |
| Tích hợp agent-core | Node dựng sẵn `agent_node(tools, system)` — cầu nối chính thức giữa 2 package (giờ mỗi feature tự lắp). |
| Test | Chỉ có `test_run.py` + `test_api.py`. Thêm test cho config merging, journal resume, registry entry-points, node abort/soft-fail. |

## Xuyên suốt cả 3 package

- Chuẩn hóa observability: `emit(channel, msg)` của graphrun, callback của agent-core, journal của fs_tools nên dùng chung một interface event.
- Ví dụ đầu-cuối: một feature mẫu "sắp xếp ảnh trong ./inbox" ghép cả 3 package (README nào cũng nhắc use case này nhưng chưa có demo chạy được).
- CI: chạy `pytest` cho cả 3 package, ruff/mypy, matrix Python 3.10–3.12.
- Typing: thêm `py.typed` marker cho từng package để consumer nhận type hints.
