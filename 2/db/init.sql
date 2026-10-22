CREATE TABLE IF NOT EXISTS processed_numbers (
    id         SERIAL PRIMARY KEY,
    num        BIGINT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
