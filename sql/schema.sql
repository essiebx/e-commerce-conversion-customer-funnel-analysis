CREATE TABLE IF NOT EXISTS ecommerce_funnel_events (
    event_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    campaign VARCHAR(100) NOT NULL,
    channel VARCHAR(100) NOT NULL,
    device VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NOT NULL,
    cart_value NUMERIC(12, 2) DEFAULT 0,
    revenue NUMERIC(12, 2) DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_funnel_user_stage
ON ecommerce_funnel_events (user_id, stage);
