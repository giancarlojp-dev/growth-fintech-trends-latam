
-- Growth by country and keyword

WITH ranked_data AS (
    SELECT
        country_code,
        keyword,
        date,
        interest_score,
        FIRST_VALUE(interest_score) OVER (
            PARTITION BY country_code, keyword
            ORDER BY date
        ) AS first_value,
        LAST_VALUE(interest_score) OVER (
            PARTITION BY country_code, keyword
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_value
    FROM fintech_trends
)

SELECT
    country_code,
    keyword,
    ROUND(
        (last_value - first_value)::numeric / NULLIF(first_value, 0),
        4
    ) AS growth_rate
FROM ranked_data
GROUP BY country_code, keyword, first_value, last_value
ORDER BY growth_rate DESC;