CREATE TABLE IF NOT EXISTS user_teams (
  user_id UUID NOT NULL,
  team_id UUID NOT NULL,
  PRIMARY KEY (user_id, team_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
); 