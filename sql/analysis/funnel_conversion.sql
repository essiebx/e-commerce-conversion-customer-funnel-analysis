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
    *,
    ROUND(100.0 * product_view_users / NULLIF(landing_users, 0), 2) AS landing_to_product_view_pct,
    ROUND(100.0 * cart_users / NULLIF(product_view_users, 0), 2) AS product_view_to_cart_pct,
    ROUND(100.0 * checkout_users / NULLIF(cart_users, 0), 2) AS cart_to_checkout_pct,
    ROUND(100.0 * purchase_users / NULLIF(checkout_users, 0), 2) AS checkout_to_purchase_pct,
    ROUND(100.0 * purchase_users / NULLIF(landing_users, 0), 2) AS landing_to_purchase_pct
FROM funnel;
