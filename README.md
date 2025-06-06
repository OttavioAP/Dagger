Git clone git@github.com:OttavioAP/Dagger.git
Cd Dagger
echo 'LLM_API_KEY=VALID_OPENROUTER_KEY' > .env
sudo docker-compose up --build
Login username =  Ianeta password = any, (project lacks auth)
http://localhost:3000/login for UI,  http://localhost:8080/docs for Fastapi OpenAPI docs

Database will ingest demo data upon startup. Nothing neesd to be done to set that up

Design Documention is Design.md