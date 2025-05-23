CREATE TABLE IF NOT EXISTS week (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary TEXT,
    feedback TEXT,
    collaborators UUID[],
    missed_deadlines UUID[],
    completed_tasks UUID[],
    points_completed INT
);
