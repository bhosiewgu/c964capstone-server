uvicorn main:app --reload --port=8000 --host=0.0.0.0 --lifespan off

docker compose up --build

pip freeze > requirements.txt

pip install -r requirements.txt


docker build -t bhosiewgu/c964capstone:1.0.0 .
docker run -p 8000:8000 bhosiewgu/c964capstone:1.0.0

docker build -t bhosiewgu/c964capstone:1.0.0-prod .
docker run -p 8000:8000 -e API_URL="https://c964capstone-3cdvungrkq-uc.a.run.app" bhosiewgu/c964capstone:1.0.0-prod


docker login  -u bhosiewgu
docker push bhosiewgu/c964capstone:1.0.0