WITH stage_counts AS (
    SELECT stage, COUNT(DISTINCT user_id) AS users
    FROM ecommerce_funnel_events
    GROUP BY stage
)
SELECT
    stage,
    users,
    LAG(users) OVER (
        ORDER BY CASE stage
            WHEN 'landing' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'cart' THEN 3
            WHEN 'checkout' THEN 4
            WHEN 'purchase' THEN 5
        END
    ) AS previous_stage_users,
    users - LAG(users) OVER (
        ORDER BY CASE stage
            WHEN 'landing' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'cart' THEN 3
            WHEN 'checkout' THEN 4
            WHEN 'purchase' THEN 5
        END
    ) AS change
FROM stage_counts;
