update-site:
	poetry run python model_3/extract_data.py
	poetry run python model_3/render.py

docker-generate:
	docker build -t model-3:latest .
	docker run --name m3 model-3:latest make update-site
	docker cp m3:/app/docs ./
	docker rm m3
