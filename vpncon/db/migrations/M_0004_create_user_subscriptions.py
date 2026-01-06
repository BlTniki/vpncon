scripts = ["""
CREATE TABLE IF NOT EXISTS user_subscriptions (
    user_id BIGINT NOT NULL,
    subscription_id BIGINT NOT NULL,
    expiry_date DATE NOT NULL,

    PRIMARY KEY (user_id)
);
""","""

CREATE TABLE IF NOT EXISTS user_subscriptions_history (
    user_id BIGINT NOT NULL,
    subscription_id BIGINT NOT NULL,
    expiry_date DATE NOT NULL,

    action CHAR(1) NOT NULL CHECK (action IN ('I','U','D')),
    valid_to TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""","""

CREATE TRIGGER user_subscriptions_history_trigger
AFTER INSERT OR UPDATE OR DELETE
ON user_subscriptions
FOR EACH ROW
EXECUTE FUNCTION log_table_history();
"""
]