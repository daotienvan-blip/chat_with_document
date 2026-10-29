#!/usr/bin/env bash
# S8-06 — kiểm biên mạng trên stack `make prod-up`. Dùng: proxy-test.sh https://localhost:8443
# Kiểm allowlist bằng cách gọi từ mạng `cwd-prod_probe` (100.64.10.0/24, ngoài allowlist) của compose.prod.local.yaml.
set -uo pipefail
URL=${1:-https://localhost:8443}
CA=$(dirname "$0")/../../var/prod-local/certs/tls.crt
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0
ok()  { echo "  ✓ $1"; pass=$((pass+1)); }
bad() { echo "  ✗ $1"; fail=$((fail+1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
C=(curl -s --cacert "$CA")

# 1. TLS
check "TLS 1.2+ được chấp nhận" '"${C[@]}" --tlsv1.2 -o /dev/null "$URL/readyz"'
check "TLS 1.1 bị từ chối" '! "${C[@]}" --tlsv1.1 --tls-max 1.1 -o /dev/null "$URL/readyz" 2>/dev/null'

# 2. Tiêu đề bảo mật, không lộ phiên bản
"${C[@]}" -D "$TMP/h" -o /dev/null "$URL/"
H=$(tr -d '\r' < "$TMP/h")
check "CSP default-src 'self'; frame-ancestors 'none'" 'grep -qi "^content-security-policy: default-src '"'"'self'"'"'; frame-ancestors '"'"'none'"'"'" <<<"$H"'
check "X-Content-Type-Options: nosniff" 'grep -qi "^x-content-type-options: nosniff" <<<"$H"'
check "Referrer-Policy: no-referrer" 'grep -qi "^referrer-policy: no-referrer" <<<"$H"'
check "Server không lộ phiên bản ($(grep -i '^server:' <<<"$H"))" '! grep -qiE "^server:.*[0-9]" <<<"$H"'
check "không có CORS" '! "${C[@]}" -D - -o /dev/null -H "Origin: https://evil.example" "$URL/api/v1/config" | grep -qi access-control-allow'

# 3. X-Request-Id do proxy đặt, ghi đè giá trị client
RID=$("${C[@]}" -D - -o /dev/null -H "X-Request-Id: gia-mao" "$URL/api/v1/config" | tr -d '\r' | awk -F': ' 'tolower($1)=="x-request-id"{print $2}')
check "X-Request-Id bị ghi đè (nhận: $RID)" '[[ "$RID" =~ ^[0-9a-f]{32}$ ]]'

# 4. 413 problem+json (tệp thưa 220 MB, không tốn đĩa)
dd if=/dev/zero of="$TMP/big.pdf" bs=1 count=0 seek=220m 2>/dev/null
"${C[@]}" -o "$TMP/b413" -D "$TMP/h413" -F "file=@$TMP/big.pdf;type=application/pdf" "$URL/api/v1/documents"
check "413 → problem+json FILE_TOO_LARGE có requestId" \
  'grep -qi "^content-type: application/problem+json" "$TMP/h413" && grep -q "\"status\":413" "$TMP/b413" && grep -q "\"code\":\"FILE_TOO_LARGE\"" "$TMP/b413" && grep -qE "\"requestId\":\"[0-9a-f]{32}\"" "$TMP/b413"'

# 4b. F-03: câu hỏi quá dài — thân > 64k bị proxy chặn; 5.000 ký tự qua proxy, api chặn ở giới hạn cứng 4.000
python3 -c 'import json; print(json.dumps({"question": "x" * 100000}))' > "$TMP/q100k.json"
"${C[@]}" -o "$TMP/bq1" -D "$TMP/hq1" -H 'Content-Type: application/json' --data-binary @"$TMP/q100k.json" "$URL/api/v1/questions"
check "câu hỏi 100 KB → proxy trả 400 QUESTION_TOO_LONG problem+json" \
  'grep -q "^HTTP/[0-9.]* 400" "$TMP/hq1" && grep -qi "^content-type: application/problem+json" "$TMP/hq1" && grep -q "\"code\":\"QUESTION_TOO_LONG\"" "$TMP/bq1" && grep -qE "\"requestId\":\"[0-9a-f]{32}\"" "$TMP/bq1"'
"${C[@]}" -o "$TMP/bq2" -H 'Content-Type: application/json' -d "{\"question\":\"$(printf 'x%.0s' $(seq 1 5000))\"}" "$URL/api/v1/questions"
check "câu hỏi 5.000 ký tự → api trả QUESTION_TOO_LONG, limit 4000" \
  'grep -q "\"code\":\"QUESTION_TOO_LONG\"" "$TMP/bq2" && grep -q "\"limit\":4000" "$TMP/bq2"'

# 5. 429 sau khi vượt hạn mức câu hỏi (30/phút, burst 5)
got429=""
for i in $(seq 1 12); do
  code=$("${C[@]}" -o "$TMP/b429" -D "$TMP/h429" -w '%{http_code}' -H 'Content-Type: application/json' \
         -d '{"question":"kiểm tra hạn mức"}' "$URL/api/v1/questions")
  [[ $code == 429 ]] && { got429=1; break; }
done
check "429 sau $i yêu cầu → problem+json RATE_LIMITED, có Retry-After" \
  '[[ -n "$got429" ]] && grep -qi "^content-type: application/problem+json" "$TMP/h429" && grep -qi "^retry-after:" "$TMP/h429" && grep -q "\"code\":\"RATE_LIMITED\"" "$TMP/b429"'
python3 - "$TMP/b413" "$TMP/b429" "$TMP/bq1" "$TMP/bq2" <<'PY' && ok "thân 413/429/400 là JSON hợp lệ đủ trường bắt buộc" || bad "thân 413/429/400 là JSON hợp lệ đủ trường bắt buộc"
import json, sys
for p in sys.argv[1:]:
    d = json.load(open(p))
    assert {"type", "title", "status", "code", "requestId"} <= d.keys(), d
PY

# 6. /metrics chỉ cho mạng hạ tầng; địa chỉ ngoài allowlist bị chặn
check "/metrics từ máy dev → 403" '[[ $("${C[@]}" -o /dev/null -w "%{http_code}" "$URL/metrics") == 403 ]]'
if docker network inspect cwd-prod_probe >/dev/null 2>&1; then
  OUT=$(docker run --rm --network cwd-prod_probe cwd-server:local python -c '
import ssl, urllib.request, urllib.error
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
try: print(urllib.request.urlopen("https://proxy:8443/", context=ctx).status)
except urllib.error.HTTPError as e: print(e.code)' 2>/dev/null | tail -1)
  check "truy cập từ 100.64.10.0/24 (ngoài allowlist) → 403 (nhận: $OUT)" '[[ "$OUT" == 403 ]]'
fi

echo; echo "Đạt $pass, lỗi $fail."
[[ $fail == 0 ]]
