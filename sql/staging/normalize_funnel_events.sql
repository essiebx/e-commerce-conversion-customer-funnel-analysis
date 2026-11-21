-- Staging query for a normalized ecommerce_funnel_events table.
-- Validate types and retain only supported funnel stages.
SELECT
    event_id,
    user_id,
    session_id,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    campaign,
    channel,
    device,
    stage,
    CAST(cart_value AS NUMERIC(12, 2)) AS cart_value,
    CAST(revenue AS NUMERIC(12, 2)) AS revenue
FROM ecommerce_funnel_events
WHERE stage IN ('landing', 'product_view', 'cart', 'checkout', 'purchase');
