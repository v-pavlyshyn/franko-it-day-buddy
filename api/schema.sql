-- Messages table (SQL backend)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user','assistant')),
    text TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- FAQ table (optional)
CREATE TABLE IF NOT EXISTS faq (
    id SERIAL PRIMARY KEY,
    category TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
);
