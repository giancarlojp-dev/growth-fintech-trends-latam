-- =========================================
-- VIEW 1: Average interest by country
-- =========================================

CREATE OR REPLACE VIEW vw_country_avg_interest AS
SELECT
    country_code,
    AVG(interest_score) AS avg_interest,
    STDDEV(interest_score) AS volatility
FROM fintech_trends
GROUP BY country_code;


-- =========================================
-- VIEW 2: Average interest by keyword
-- =========================================

CREATE OR REPLACE VIEW vw_keyword_avg_interest AS
SELECT
    keyword,
    AVG(interest_score) AS avg_interest,
    STDDEV(interest_score) AS volatility
FROM fintech_trends
GROUP BY keyword;


-- =========================================
-- VIEW 3: Monthly aggregated trend
-- =========================================

CREATE OR REPLACE VIEW vw_monthly_trends AS
SELECT
    DATE_TRUNC('month', date) AS month,
    country_code,
    keyword,
    AVG(interest_score) AS monthly_avg
FROM fintech_trends
GROUP BY month, country_code, keyword
ORDER BY month;