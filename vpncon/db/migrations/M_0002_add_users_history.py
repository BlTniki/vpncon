scripts = ["""
CREATE OR REPLACE FUNCTION log_table_history()
RETURNS TRIGGER AS $$
DECLARE
    hist_table TEXT := TG_TABLE_NAME || '_history';
    cols TEXT;
    sql TEXT;
BEGIN
    -- формируем список колонок таблицы (кроме служебных)
    SELECT string_agg(quote_ident(column_name), ', ')
    INTO cols
    FROM information_schema.columns
    WHERE table_name = TG_TABLE_NAME
      AND table_schema = TG_TABLE_SCHEMA;

    IF TG_OP = 'INSERT' THEN
        sql := format(
            'INSERT INTO %%I (%%s, action)
                SELECT %%s, %%L
                FROM (SELECT ($1).* ) AS t',
            hist_table, cols, cols, 'I'
        );
        EXECUTE sql USING NEW;
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        sql := format(
            'INSERT INTO %%I (%%s, action)
            SELECT %%s, %%L
            FROM (SELECT ($1).* ) AS t',
            hist_table, cols, cols, 'U'
        );
        EXECUTE sql USING OLD;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        sql := format(
            'INSERT INTO %%I (%%s, action)
             SELECT %%s, %%L
            FROM (SELECT ($1).* ) AS t',
            hist_table, cols, cols, 'D'
        );
        EXECUTE sql USING OLD;
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql
;
""","""

CREATE TABLE IF NOT EXISTS users_history (
    telegram_id BIGINT,
    telegram_nick VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,

    action CHAR(1) NOT NULL CHECK (action IN ('I','U','D')),
    valid_to TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (telegram_id, valid_to)
)
;
""","""

CREATE TRIGGER users_history_trigger
AFTER INSERT OR UPDATE OR DELETE
ON users
FOR EACH ROW
EXECUTE FUNCTION log_table_history()
;
"""
]