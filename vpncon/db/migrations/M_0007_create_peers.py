scripts = ["""
CREATE TABLE IF NOT EXISTS peers (
    user_id BIGINT NOT NULL,
    host_id BIGINT NOT NULL,
    conf_name VARCHAR(255) NOT NULL,
    peer_ip VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL,

    PRIMARY KEY (user_id, conf_name),
    UNIQUE (host_id, peer_ip)
);
""","""

CREATE TABLE IF NOT EXISTS peers_history (
    user_id BIGINT NOT NULL,
    host_id BIGINT NOT NULL,
    conf_name VARCHAR(255) NOT NULL,
    peer_ip VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL,

    action CHAR(1) NOT NULL CHECK (action IN ('I','U','D')),
    valid_to TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""","""

CREATE TRIGGER peers_history_trigger
AFTER INSERT OR UPDATE OR DELETE
ON peers
FOR EACH ROW
EXECUTE FUNCTION log_table_history();
"""
]