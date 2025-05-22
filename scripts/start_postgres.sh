#!/bin/bash
set -e



# Start Postgres container if not running
if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        # cleanup
        docker rm $CONTAINER_NAME
    fi
    docker run --name $CONTAINER_NAME -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_DB=$POSTGRES_DB -p $POSTGRES_PORT:5432 -d postgres:15
fi

# Wait for Postgres to be ready
until docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER; do
  echo "Waiting for postgres..."
  sleep 2
done

echo "Postgres is ready. Applying schema."
# Copy schema files into container and apply
SCHEMA_PATH_USER="/tmp/user.sql"
SCHEMA_PATH_TEAM="/tmp/team.sql"
SCHEMA_PATH_USER_TEAMS="/tmp/user_teams.sql"
SCHEMA_PATH_TASKS="/tmp/tasks.sql"
SCHEMA_PATH_USER_TASKS="/tmp/user_tasks.sql"
SCHEMA_PATH_DAGS="/tmp/dags.sql"
SCHEMA_PATH_DAG="/tmp/dag.sql"
docker cp db/schema/user.sql $CONTAINER_NAME:$SCHEMA_PATH_USER
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_USER
docker cp db/schema/team.sql $CONTAINER_NAME:$SCHEMA_PATH_TEAM
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_TEAM
docker cp db/schema/user_teams.sql $CONTAINER_NAME:$SCHEMA_PATH_USER_TEAMS
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_USER_TEAMS
docker cp db/schema/tasks.sql $CONTAINER_NAME:$SCHEMA_PATH_TASKS
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_TASKS
docker cp db/schema/user_tasks.sql $CONTAINER_NAME:$SCHEMA_PATH_USER_TASKS
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_USER_TASKS
docker cp db/schema/dags.sql $CONTAINER_NAME:$SCHEMA_PATH_DAGS
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_DAGS
docker cp db/schema/dag.sql $CONTAINER_NAME:$SCHEMA_PATH_DAG
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH_DAG

# Ingest example user data if present
if [ -f "db/example_data/init_users.sql" ]; then
  docker cp db/example_data/init_users.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_users.sql
fi

# Ingest example team data if present
if [ -f "db/example_data/init_teams.sql" ]; then
  docker cp db/example_data/init_teams.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_teams.sql
fi

# Ingest example user_teams data if present
if [ -f "db/example_data/init_user_teams.sql" ]; then
  docker cp db/example_data/init_user_teams.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_user_teams.sql
fi

# Ingest example tasks data if present
if [ -f "db/example_data/init_tasks.sql" ]; then
  docker cp db/example_data/init_tasks.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_tasks.sql
fi

# Ingest example user_tasks data if present
if [ -f "db/example_data/init_user_tasks.sql" ]; then
  docker cp db/example_data/init_user_tasks.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_user_tasks.sql
fi

# Ingest example dags data if present
if [ -f "db/example_data/init_dags.sql" ]; then
  docker cp db/example_data/init_dags.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_dags.sql
fi

# Ingest example dag data if present
if [ -f "db/example_data/init_dag.sql" ]; then
  docker cp db/example_data/init_dag.sql $CONTAINER_NAME:/tmp/
  docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f /tmp/init_dag.sql
fi

# Ingest additional team data if present
if [ -d "db/example_data/teams" ]; then
  for f in db/example_data/teams/*.sql; do
    [ -e "$f" ] || continue
    docker cp "$f" $CONTAINER_NAME:/tmp/
    docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f "/tmp/$(basename $f)"
  done
fi 