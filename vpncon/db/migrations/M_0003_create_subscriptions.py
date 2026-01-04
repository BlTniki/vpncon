scripts = ["""
CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGINT PRIMARY KEY,
    price_in_rub NUMERIC(12,2) NOT NULL,
    allowed_peers INT NOT NULL,
    period INTERVAL NOT NULL,
    role VARCHAR(255) NOT NULL
);
""","""

CREATE TABLE IF NOT EXISTS subscriptions_history (
    id BIGINT,
    price_in_rub NUMERIC(12,2) NOT NULL,
    allowed_peers INT NOT NULL,
    period INTERVAL NOT NULL,
    role VARCHAR(255) NOT NULL,

    action CHAR(1) NOT NULL CHECK (action IN ('I','U','D')),
    valid_to TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (id, valid_to)
);
""","""

CREATE TRIGGER subscriptions_history_trigger
AFTER INSERT OR UPDATE OR DELETE
ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION log_table_history();
"""
]