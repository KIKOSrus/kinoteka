-- Выполнить от имени суперпользователя postgres, например:
--   sudo -u postgres psql -f init_db.sql

CREATE USER kinoteka WITH PASSWORD 'kinoteka';
CREATE DATABASE kinoteka OWNER kinoteka;
GRANT ALL PRIVILEGES ON DATABASE kinoteka TO kinoteka;
