-- Sample SQL for dqgate static review (intentional issues for demo).

SELECT *
FROM raw_events
WHERE event_date = CURRENT_DATE;

DELETE FROM staging_events;

SELECT
    user_id,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn
FROM users
WHERE is_active = TRUE;
