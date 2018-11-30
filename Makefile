bootstrap:
	sudo pip install poetry==0.12.10

install:
	poetry install

update-data:
	poetry run python model_3/extract_data.py
	poetry run python model_3/render.py
