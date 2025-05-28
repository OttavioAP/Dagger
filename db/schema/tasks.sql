CREATE TYPE task_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY');
CREATE TYPE task_focus AS ENUM ('LOW', 'MEDIUM', 'HIGH');

CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_name TEXT NOT NULL,
  team_id UUID NOT NULL REFERENCES teams(id),
  deadline TIMESTAMPTZ,
  points INT,
  priority task_priority NOT NULL DEFAULT 'LOW',
  focus task_focus NOT NULL DEFAULT 'LOW',
  date_of_completion TIMESTAMPTZ,
  date_of_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  description TEXT,
  notes TEXT
); 