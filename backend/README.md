# API Service
* cooking rescipee system
# Documentation
* Swagger: http://localhost:5000/apidocs/
## Prerequisites

* Python 3.7
* Postgres
* FLASGGER
* Docker

Development Tool:

* `mypy`: Type hinting support
* `black`: Python formatter
* `pylint`: Linter

# Development Setup
1. Install dependencies:
```
pip install requirements.txt
```
---------------------------------------------------------------
2. Setup `.env` file
```
virtualenv -p `which python3` .venv
source .venv/bin/activate
pip install -r requirements.txt
```
---------------------------------------------------------------
3. Setup database
```
docker run --name db -p 127.0.0.1:5432:5432 -e POSTGRES_USER=<NAME> -e POSTGRES_PASSWORD=<PSWD> -e POSTGRES_DB=<db_name> -d postgres:11.1
docker start db
python manage.py db upgrade
```
* If need POSTGIS created pgdb vanillaly
---------------------------------------------------------------
4. (Optional) access Postgres database
```
psql "postgresql://:@localhost:5432/<db_name>"
```
---------------------------------------------------------------
5. Set up redis
```
docker run --name redis -p 127.0.0.1:6379:6379 -d redis:4.0.9
```
---------------------------------------------------------------
6. (Optional) access Redis database
```
redis-cli -h 127.0.0.1 -p 6379 -n 0
```
---------------------------------------------------------------
7. Start Celery worker:
```
python main_celery.py worker --loglevel=info -Ofair --beat
```
---------------------------------------------------------------
8. Start project
```
python main.py
```
# SERVER SETUP
1. Set up docker on ubuntu 18.04
```
sudo apt-get update
sudo apt-get remove docker docker-engine docker.io
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```
2. Backend deploy
```
cd <repo directory>
sudo make deploy-server
```