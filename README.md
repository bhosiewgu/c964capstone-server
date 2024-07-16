uvicorn main:app --reload --port=8000 --host=0.0.0.0 --lifespan off

docker compose up --build

pip freeze > requirements.txt

pip install -r requirements.txt


docker run -p 8000:8000 bhosiewgu/c964capstone:1.0.0


docker login  -u bhosiewgu
docker build -t bhosiewgu/c964capstone:1.0.0 .
docker push bhosiewgu/c964capstone:1.0.0