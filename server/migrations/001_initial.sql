CREATE TABLE IF NOT EXISTS voters (
    roll TEXT PRIMARY KEY,
    wallet TEXT UNIQUE NOT NULL,
    encoding BYTEA NOT NULL
);
CREATE TABLE IF NOT EXISTS challenges (
    nonce TEXT PRIMARY KEY,
    roll TEXT NOT NULL,
    wallet TEXT NOT NULL,
    message TEXT NOT NULL,
    expires BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS challenges_expiry_idx ON challenges (expires);
