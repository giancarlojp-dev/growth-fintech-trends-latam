-- Fintecth Trends LATAM / DATABASE

CREATE TABLE IF NOT EXISTS fintech_trends (

    id BIGSERIAL PRIMARY KEY,

    date DATE NOT NULL,
    country_code VARCHAR(5) NOT NULL,
    keyword VARCHAR(100) NOT NULL,

    interest_score SMALLINT NOT NULL CHECK (interest_score BETWEEN 0 AND 100),

    z_score FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--- INDEX
CREATE INDEX IF NOT EXISTS idx_trends_date 
ON fintech_trends(date);

CREATE INDEX IF NOT EXISTS idx_trends_country 
ON fintech_trends(country_code);

CREATE INDEX IF NOT EXISTS idx_trends_keyword 
ON fintech_trends(keyword);

CREATE INDEX IF NOT EXISTS idx_trends_country_keyword            
ON fintech_trends(country_code, keyword);


