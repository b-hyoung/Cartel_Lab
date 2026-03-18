#!/bin/sh
set -e

echo "DB 연결 대기 중..."
until python -c "
import pymysql, os, sys, traceback, urllib.parse as up
mysql_url = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL', '')
if mysql_url:
    u = up.urlparse(mysql_url)
    host, user, password, db, port = u.hostname, u.username, u.password, u.path.lstrip('/'), u.port or 3306
else:
    host     = os.getenv('DB_HOST')     or os.getenv('MYSQL_HOST',     'db')
    user     = os.getenv('DB_USER')     or os.getenv('MYSQL_USER',     'root')
    password = os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD', '')
    db       = os.getenv('DB_NAME')     or os.getenv('MYSQL_DATABASE', 'cartel_lab')
    port     = int(os.getenv('DB_PORT') or os.getenv('MYSQL_PORT', 3306))
print(f'DB 접속 시도: host={host}, port={port}, user={user}, db={db}', flush=True)
try:
    pymysql.connect(host=host, user=user, password=str(password), db=db, port=int(port), connect_timeout=5)
    sys.exit(0)
except Exception as e:
    print('DB 연결 실패:', repr(e), flush=True)
    traceback.print_exc()
    sys.exit(1)
"; do
  echo "DB 준비 안됨, 2초 후 재시도..."
  sleep 2
done

echo "DB 연결 성공!"

python manage.py migrate --noinput
echo "migrate 완료"

python manage.py shell -c "
import os
from users.models import User
sid = os.environ.get('ADMIN_ID', '')
pw  = os.environ.get('ADMIN_PASSWORD', '')
if sid and pw:
    if not User.objects.filter(student_id=sid).exists():
        User.objects.create_superuser(student_id=sid, password=pw, name=os.environ.get('ADMIN_NAME', '관리자'))
        print('관리자 계정 생성됨:', sid)
    else:
        print('관리자 계정 이미 존재:', sid)
else:
    print('ADMIN_ID / ADMIN_PASSWORD 미설정, 건너뜀')
"

echo "공고 수집 시작 (백그라운드)..."
python manage.py sync_job_sources &

if [ $# -gt 0 ]; then
  exec "$@"
else
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 300 \
    --graceful-timeout 30
fi
