#!/usr/bin/env bash
# Демонстрация API через cURL. Запуск: ./demo.sh [BASE_URL]   (по умолчанию http://localhost — через nginx)
# Требуется: curl, python3. БД должна быть заполнена: python seed.py
BASE=${1:-http://localhost}
J='Content-Type: application/json'
tok() { python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])"; }
step() { echo; echo "### $*"; }

step "POST /register"
U=demo$RANDOM
curl -s -X POST $BASE/register -H "$J" -d "{\"username\":\"$U\",\"email\":\"$U@example.com\",\"password\":\"secret1\"}"; echo

step "POST /login (user)"
TOKEN=$(curl -s -X POST $BASE/login -H "$J" -d "{\"username\":\"$U\",\"password\":\"secret1\"}" | tok)
echo "JWT: ${TOKEN:0:40}..."
A="Authorization: Bearer $TOKEN"

step "GET /movies без токена -> 401"
curl -s -w " [%{http_code}]\n" $BASE/movies

step "GET /me"
curl -s $BASE/me -H "$A"; echo

step "GET /movies?genre=Фантастика"
curl -s -G $BASE/movies -H "$A" --data-urlencode "genre=Фантастика"; echo

step "POST /movies от обычного пользователя -> 403"
curl -s -w " [%{http_code}]\n" -X POST $BASE/movies -H "$A" -H "$J" -d '{"title":"X"}'

step "POST /login (admin) и POST /movies -> 201"
AT=$(curl -s -X POST $BASE/login -H "$J" -d '{"username":"admin","password":"admin12345"}' | tok)
AA="Authorization: Bearer $AT"
MOVIE=$(curl -s -X POST $BASE/movies -H "$AA" -H "$J" \
  -d '{"title":"Побег из Шоушенка","release_year":1994,"director":"Фрэнк Дарабонт","duration_minutes":142,"genres":["Драма"]}')
echo "$MOVIE"
MID=$(echo "$MOVIE" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

step "PATCH /movies/$MID"
curl -s -X PATCH $BASE/movies/$MID -H "$AA" -H "$J" -d '{"description":"Классика."}'; echo

step "POST /library — добавить фильм в свою библиотеку, GET /library"
curl -s -o /dev/null -w "[%{http_code}]\n" -X POST $BASE/library -H "$A" -H "$J" -d "{\"movie_id\":$MID}"
curl -s $BASE/library -H "$A"; echo

step "POST /playlists, PUT /playlists/{id}/save"
PL=$(curl -s -X POST $BASE/playlists -H "$A" -H "$J" -d "{\"name\":\"Мой плейлист\",\"movie_ids\":[$MID]}")
echo "$PL"
PID=$(echo "$PL" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")
curl -s -o /dev/null -w "save [%{http_code}]\n" -X PUT $BASE/playlists/$PID/save -H "$AA"
curl -s $BASE/playlists/saved -H "$AA"; echo

step "DELETE /playlists/$PID и DELETE /movies/$MID"
curl -s -o /dev/null -w "[%{http_code}]\n" -X DELETE $BASE/playlists/$PID -H "$A"
curl -s -o /dev/null -w "[%{http_code}]\n" -X DELETE $BASE/movies/$MID -H "$AA"
