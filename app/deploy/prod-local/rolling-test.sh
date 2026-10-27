#!/usr/bin/env bash
# S8-05 — thử nâng cấp cuốn chiếu trên stack `make prod-up`. Dùng: rolling-test.sh <document-id> (PDF lớn, đã ready)
#  A. Qua proxy: tải chậm, `docker stop` một bản api giữa chừng ⇒ tải xong đủ byte; yêu cầu mới vẫn 200.
#     (nginx đệm phản hồi nên api thường đã giao xong cho proxy — đây là hành vi mong muốn.)
#  B. Gọi thẳng một bản api bằng client đọc chậm (không qua bộ đệm nginx), gửi SIGTERM giữa chừng
#     ⇒ uvicorn chờ yêu cầu xong (--timeout-graceful-shutdown 45) rồi mới thoát mã 0.
#  C. Dừng cả hai bản ⇒ proxy trả 502 problem+json. Cuối cùng khởi động lại.
set -uo pipefail
DOC=$1
URL=${URL:-https://localhost:8443}
CA=$(dirname "$0")/../../var/prod-local/certs/tls.crt
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
C=(curl -s --cacert "$CA")
pass=0; fail=0
check() { if eval "$2"; then echo "  ✓ $1"; pass=$((pass+1)); else echo "  ✗ $1"; fail=$((fail+1)); fi; }
wait_ready() { for i in $(seq 1 60); do
  [[ $(docker inspect -f '{{.State.Health.Status}}' "$1") == healthy ]] && return 0; sleep 1; done; return 1; }

"${C[@]}" -o "$TMP/ref.pdf" "$URL/api/v1/documents/$DOC/file"
SIZE=$(wc -c < "$TMP/ref.pdf" | tr -d ' '); SHA=$(shasum -a 256 "$TMP/ref.pdf" | cut -d' ' -f1)
echo "Tệp mẫu: $SIZE byte"

echo "A. Qua proxy, dừng cwd-prod-api-1 giữa lúc tải"
"${C[@]}" --limit-rate $((SIZE / 8)) -o "$TMP/slow.pdf" -w '%{http_code}' "$URL/api/v1/documents/$DOC/file" > "$TMP/code" &
DL=$!; sleep 2
docker stop -t 50 cwd-prod-api-1 >/dev/null & STOP=$!
sleep 1
okc=0; for i in $(seq 1 10); do [[ $("${C[@]}" -o /dev/null -w '%{http_code}' "$URL/api/v1/config") == 200 ]] && okc=$((okc+1)); done
check "trong lúc api-1 tắt: yêu cầu mới thành công $okc/10" '[[ $okc == 10 ]]'
wait $DL; wait $STOP
check "yêu cầu đang chạy hoàn tất: HTTP $(cat "$TMP/code"), đúng sha256" \
  '[[ $(cat "$TMP/code") == 200 ]] && cmp -s "$TMP/ref.pdf" "$TMP/slow.pdf"'
check "api-1 thoát mã 0" '[[ $(docker inspect -f "{{.State.ExitCode}}" cwd-prod-api-1) == 0 ]]'
docker start cwd-prod-api-1 >/dev/null; wait_ready cwd-prod-api-1

echo "B. Gọi thẳng cwd-prod-api-2 bằng client đọc chậm, SIGTERM giữa chừng"
docker run --rm --network cwd-prod_app cwd-server:local python -c '
import hashlib, sys, time, urllib.request
r = urllib.request.urlopen(sys.argv[1]); h = hashlib.sha256(); n = 0
while chunk := r.read(256 * 1024):
    h.update(chunk); n += len(chunk); time.sleep(0.15)
print(r.status, n, h.hexdigest())' "http://cwd-prod-api-2:8000/api/v1/documents/$DOC/file" > "$TMP/direct" 2>&1 &
DL=$!; sleep 4
t0=$(date +%s); docker stop -t 50 cwd-prod-api-2 >/dev/null; t1=$(date +%s)
wait $DL
read -r st n sha < "$TMP/direct"
echo "  (api-2 nhận SIGTERM, thoát sau $((t1 - t0)) s; client nhận $n byte)"
check "yêu cầu đang chạy hoàn tất khi api nhận SIGTERM: HTTP $st, đủ byte, đúng sha256" \
  '[[ "$st" == 200 && "$n" == "$SIZE" && "$sha" == "$SHA" ]]'
check "api-2 chờ yêu cầu xong mới thoát (≥ 2 s) và thoát mã 0" \
  '(( t1 - t0 >= 2 )) && [[ $(docker inspect -f "{{.State.ExitCode}}" cwd-prod-api-2) == 0 ]]'

echo "C. Không còn bản api nào"
docker stop -t 50 cwd-prod-api-1 >/dev/null
"${C[@]}" -o "$TMP/b502" -D "$TMP/h502" "$URL/api/v1/config"
check "proxy trả 502 problem+json có requestId" \
  'grep -q " 502" "$TMP/h502" && grep -qi "^content-type: application/problem+json" "$TMP/h502" && grep -qE "\"requestId\":\"[0-9a-f]{32}\"" "$TMP/b502"'
docker start cwd-prod-api-1 cwd-prod-api-2 >/dev/null
wait_ready cwd-prod-api-1; wait_ready cwd-prod-api-2
check "khởi động lại: readyz 200 qua proxy" '[[ $("${C[@]}" -o /dev/null -w "%{http_code}" "$URL/readyz") == 200 ]]'

echo; echo "Đạt $pass, lỗi $fail."
[[ $fail == 0 ]]
