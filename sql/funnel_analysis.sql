WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN stage = 'landing' THEN user_id END) AS landing_users,
        COUNT(DISTINCT CASE WHEN stage = 'product_view' THEN user_id END) AS product_view_users,
        COUNT(DISTINCT CASE WHEN stage = 'cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN stage = 'checkout' THEN user_id END) AS checkout_users,
        COUNT(DISTINCT CASE WHEN stage = 'purchase' THEN user_id END) AS purchase_users,
        SUM(CASE WHEN stage = 'purchase' THEN revenue ELSE 0 END) AS purchase_revenue
    FROM ecommerce_funnel_events
)
SELECT
    landing_users,
    product_view_users,
    cart_users,
    checkout_users,
    purchase_users,
    ROUND(100.0 * purchase_users / NULLIF(landing_users, 0), 2) AS landing_to_purchase_pct,
    ROUND(100.0 * checkout_users / NULLIF(cart_users, 0), 2) AS cart_to_checkout_pct,
    ROUND(100.0 * purchase_users / NULLIF(checkout_users, 0), 2) AS checkout_to_purchase_pct,
    purchase_revenue
FROM funnel;

-- Stage-level drop-off
WITH stage_counts AS (
    SELECT stage, COUNT(DISTINCT user_id) AS users
    FROM ecommerce_funnel_events
    GROUP BY stage
)
SELECT
    stage,
    users,
    LAG(users) OVER (ORDER BY CASE stage
        WHEN 'landing' THEN 1
        WHEN 'product_view' THEN 2
        WHEN 'cart' THEN 3
        WHEN 'checkout' THEN 4
        WHEN 'purchase' THEN 5
    END) AS previous_stage_users,
    users - LAG(users) OVER (ORDER BY CASE stage
        WHEN 'landing' THEN 1
        WHEN 'product_view' THEN 2
        WHEN 'cart' THEN 3
        WHEN 'checkout' THEN 4
        WHEN 'purchase' THEN 5
    END) AS absolute_change
FROM stage_counts;

-- Segment performance
SELECT
    campaign,
    channel,
    device,
    COUNT(DISTINCT CASE WHEN stage = 'landing' THEN user_id END) AS landing_users,
    COUNT(DINCT CASE WHEN stage = 'purchase' THEN user_id END) AS purchase_users,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN stage = 'purchase' THEN user_id END) /
          NULLIF(COUNT(DISTINCT CASE WHEN stage = 'landing' THEN user_id END), 0), 2) AS conversion_pct,
    SUM(CASE WHEN stage = 'purchase' THEN revenue ELSE 0 END) AS revenue
FROM ecommerce_funnel_events
GROUP BY campaign, channel, device
ORDER BY revenue DESC;
