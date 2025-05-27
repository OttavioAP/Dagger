#!/bin/bash

# Create types directory if it doesn't exist
mkdir -p src/types

# Generate model types from individual schema files
echo "Generating model types..."
for f in ../backend/schemas/*.json; do
  base=$(basename "$f" .json)
  if [[ "$base" != "openapi" ]]; then
    echo "Generating types for $base..."
    datamodel-codegen --input "$f" --output "src/types/$base.ts" --output-model-type typescript
  fi
done

# Generate API types from OpenAPI schema
echo "Generating API types..."
npx openapi-typescript http://localhost:8080/openapi.json -o src/types/api.ts

echo "Type generation complete!" 