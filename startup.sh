#!/bin/bash
set -e
set -x

echo 'Waiting for PostgreSQL...'
for i in $(seq 1 30); do
  PGPASSWORD=${MIGRATION_DB_PASSWORD} psql -h postgres -U schedule_migration_user -d schedule_db -c 'SELECT 1;' >/dev/null 2>&1 && break
  [ $i -eq 30 ] && echo 'Error: PostgreSQL timeout' && exit 1
  sleep 2
done

echo 'Database setup...'
cd /app

echo '1. Ensuring alembic_version table...'
PGPASSWORD=${MIGRATION_DB_PASSWORD} psql -h postgres -U schedule_migration_user -d schedule_db -c '
  CREATE TABLE IF NOT EXISTS schedule_schema.alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
  );'

echo '2. Checking current migration state...'
VERSION_COUNT=$(PGPASSWORD=${MIGRATION_DB_PASSWORD} psql -h postgres -U schedule_migration_user -d schedule_db -t -c "SELECT COUNT(*) FROM schedule_schema.alembic_version;" | tr -d '[:space:]')
echo "Version count in database: $VERSION_COUNT"

MIGRATION_FILES_COUNT=$(find alembic/versions -name "*.py" -type f 2>/dev/null | wc -l)
echo "Migration files found: $MIGRATION_FILES_COUNT"

if [ "$VERSION_COUNT" -eq 0 ]; then
  if [ "$MIGRATION_FILES_COUNT" -gt 0 ]; then
    echo '3. Database is empty but migration files exist. Stamping...'
    alembic upgrade head
    alembic stamp head
  else
    echo '3. No migration files, creating initial migration...'
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
  fi
else
  alembic upgrade head
fi

echo '5. Verifying tables...'
PGPASSWORD=${MIGRATION_DB_PASSWORD} psql -h postgres -U schedule_migration_user -d schedule_db -c "\dt schedule_schema.*"

echo 'Starting app...'
cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload