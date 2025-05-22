CREATE TABLE IF NOT EXISTS dag (
  dag_id UUID PRIMARY KEY,
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  dag_graph JSONB NOT NULL
);

-- Add dag_graph column to dag table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='dag' AND column_name='dag_graph'
    ) THEN
        ALTER TABLE dag ADD COLUMN dag_graph JSONB;
    END IF;
END$$; 