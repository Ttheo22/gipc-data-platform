CREATE TABLE IF NOT EXISTS economic_indicators (
    id               SERIAL PRIMARY KEY,
    indicator_name   VARCHAR(100) NOT NULL,
    source           VARCHAR(50)  NOT NULL,
    country          VARCHAR(100) NOT NULL,
    year             INTEGER      NOT NULL,
    value            NUMERIC(20, 6),
    unit             VARCHAR(50),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (indicator_name, source, country, year)
);

CREATE TABLE IF NOT EXISTS domestic_indicators (
    id             SERIAL PRIMARY KEY,
    indicator_name VARCHAR(100) NOT NULL,
    source         VARCHAR(50)  NOT NULL,
    country        VARCHAR(100) NOT NULL,
    year           INTEGER      NOT NULL,
    period         VARCHAR(20),
    quarter        VARCHAR(5),
    month          VARCHAR(20),
    value          NUMERIC(20, 6),
    unit           VARCHAR(50),
    notes          TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (indicator_name, source, country, period)
);