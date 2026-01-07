scripts = ["""
CREATE TABLE IF NOT EXISTS hosts (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    host_password VARCHAR(255) NOT NULL
);
""","""

CREATE TABLE IF NOT EXISTS hosts_history (
    id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    host_password VARCHAR(255) NOT NULL,

    action CHAR(1) NOT NULL CHECK (action IN ('I','U','D')),
    valid_to TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""","""

CREATE TRIGGER hosts_history_trigger
AFTER INSERT OR UPDATE OR DELETE
ON hosts
FOR EACH ROW
EXECUTE FUNCTION log_table_history();
"""
]