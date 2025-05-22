CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_name TEXT NOT NULL,
  team_id UUID NOT NULL REFERENCES teams(id),
  deadline TIMESTAMPTZ,
  points INT,
  date_of_completion TIMESTAMPTZ,
  description TEXT,
  notes TEXT,
  task_data JSONB
); 