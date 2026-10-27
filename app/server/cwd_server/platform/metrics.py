"""Số đo vận hành (S8-01). Nhãn không bao giờ chứa nội dung hay tên tài liệu."""
from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS = Counter("cwd_http_requests_total", "Yêu cầu HTTP", ["route", "method", "status"])
HTTP_LATENCY = Histogram("cwd_http_request_seconds", "Độ trễ HTTP", ["route"])
ANSWERS = Counter("cwd_answers_total", "Câu trả lời theo trạng thái", ["status"])
GROUNDING_DOWNGRADES = Counter("cwd_grounding_downgrades_total", "Số lần G-L2 hạ về not_found")
LLM_CALLS = Counter("cwd_llm_calls_total", "Lời gọi AI", ["op", "outcome"])
LLM_LATENCY = Histogram("cwd_llm_seconds", "Độ trễ AI", ["op"])
BREAKER_OPEN = Gauge("cwd_llm_breaker_open", "1 nếu circuit breaker đang mở")
JOBS = Gauge("cwd_jobs", "Số việc theo trạng thái", ["status"])
OLDEST_JOB_AGE = Gauge("cwd_oldest_queued_job_seconds", "Tuổi việc chờ lâu nhất")
JOB_DURATION = Histogram("cwd_job_seconds", "Thời lượng xử lý việc", ["type"])
