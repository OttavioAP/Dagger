CREATE TABLE IF NOT EXISTS dag (
  dag_id UUID NOT NULL REFERENCES dags(id) ON DELETE CASCADE,
  from_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  to_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  PRIMARY KEY (dag_id, from_task_id, to_task_id),
  CHECK (from_task_id <> to_task_id)
);

-- Add dag_graph column to dags table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='dags' AND column_name='dag_graph'
    ) THEN
        ALTER TABLE dags ADD COLUMN dag_graph JSONB;
    END IF;
END$$; 