-- migrate:up
CREATE TABLE leaderboard (
    id BIGSERIAL PRIMARY KEY,
    trainable_parameters NUMERIC,
    execution_time NUMERIC,
    loss NUMERIC,
    accuracy NUMERIC,
    model_size NUMERIC,
    learning_rate NUMERIC,
    batch_size NUMERIC,
    epochs NUMERIC,
    optimizer TEXT,
    email TEXT,
    experiment TEXT,
    model_name TEXT
);

-- migrate:down
DROP TABLE IF EXISTS leaderboard;
