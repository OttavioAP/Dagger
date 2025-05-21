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
# Copy schema file into container and apply
SCHEMA_PATH="/tmp/user.sql"
docker cp db/schema/user.sql $CONTAINER_NAME:$SCHEMA_PATH
docker exec -u $POSTGRES_USER $CONTAINER_NAME psql -d $POSTGRES_DB -f $SCHEMA_PATH 