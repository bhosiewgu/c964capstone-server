#!/bin/bash

rm -rf artifacts/*.pkl
rm -rf server-frontend

docker build -t bhosiewgu/c964capstone:1.0.0-prod-8015 .
docker push bhosiewgu/c964capstone:1.0.0-prod-8015

git restore --staged server-frontend
git checkout .