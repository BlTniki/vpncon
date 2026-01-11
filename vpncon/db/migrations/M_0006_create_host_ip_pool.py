scripts = ["""
CREATE TABLE host_ip_pool (
    host_id BIGINT NOT NULL,
    peer_ip VARCHAR(255) NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT false,
    PRIMARY KEY (host_id, peer_ip)
);
""","""
CREATE INDEX idx_host_ip_pool_free
ON host_ip_pool (host_id)
WHERE is_used = false;
"""]
