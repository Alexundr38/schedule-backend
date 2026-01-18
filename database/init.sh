#!/bin/bash
sed -e "s/\${SCHEDULE_DB_PASSWORD}/$SCHEDULE_DB_PASSWORD/g" \
    -e "s/\${MIGRATION_DB_PASSWORD}/$MIGRATION_DB_PASSWORD/g" \
    /app/database/init.sql | psql -U postgres