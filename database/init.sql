DO $$
BEGIN
    IF NOT EXISTS(SELECT FROM pg_catalog.pg_roles WHERE rolname = 'schedule_user') THEN
       EXECUTE format('CREATE USER schedule_user WITH PASSWORD %L', '${SCHEDULE_DB_PASSWORD}');
    ELSE
       EXECUTE format('ALTER USER schedule_user WITH PASSWORD %L', '${SCHEDULE_DB_PASSWORD}');
    END IF;

    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'schedule_migration_user') THEN
        EXECUTE format('CREATE USER schedule_migration_user WITH PASSWORD %L', '${MIGRATION_DB_PASSWORD}');
    ELSE
        EXECUTE format('ALTER USER schedule_migration_user WITH PASSWORD %L', '${MIGRATION_DB_PASSWORD}');
    END IF;
END $$;

\c schedule_db

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE TYPE schedule_schema.event_format_enum AS ENUM ('ONLINE', 'OFFLINE');

CREATE SCHEMA IF NOT EXISTS schedule_schema;

GRANT CONNECT ON DATABASE schedule_db TO schedule_user;
GRANT USAGE ON SCHEMA schedule_schema TO schedule_user;
GRANT ALL ON SCHEMA schedule_schema TO schedule_migration_user;

ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA schedule_schema GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO schedule_user;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA schedule_schema GRANT USAGE, SELECT ON SEQUENCES TO schedule_user;

ALTER DEFAULT PRIVILEGES FOR USER schedule_migration_user IN SCHEMA schedule_schema GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO schedule_user;
ALTER DEFAULT PRIVILEGES FOR USER schedule_migration_user IN SCHEMA schedule_schema GRANT USAGE, SELECT ON SEQUENCES TO schedule_user;

GRANT ALL PRIVILEGES ON DATABASE schedule_db TO schedule_migration_user;
GRANT ALL PRIVILEGES ON SCHEMA schedule_schema TO schedule_migration_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schedule_schema TO schedule_migration_user;

ALTER DEFAULT PRIVILEGES FOR USER schedule_migration_user IN SCHEMA schedule_schema GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO schedule_migration_user;
ALTER DEFAULT PRIVILEGES FOR USER schedule_migration_user IN SCHEMA schedule_schema GRANT USAGE, SELECT ON SEQUENCES TO schedule_migration_user;