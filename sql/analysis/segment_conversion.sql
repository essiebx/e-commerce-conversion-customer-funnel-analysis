SELECT
    campaign,
    channel,
    device,
    COUNT(DISTINCT CASE WHEN stage = 'landing' THEN user_id END) AS landing_users,
    COUNT(DISTINCT CASE WHEN stage = 'purchase' THEN user_id END) AS purchase_users,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN stage = 'purchase' THEN user_id END)
        / NULLIF(COUNT(DISTINCT CASE WHEN stage = 'landing' THEN user_id END), 0),
        2
    ) AS conversion_pct,
    SUM(CASE WHEN stage = 'purchase' THEN revenue ELSE 0 END) AS revenue
FROM ecommerce_funnel_events
GROUP BY campaign, channel, device
ORDER BY conversion_pct DESC;
