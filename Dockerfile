FROM joyzoursky/python-chromedriver:3.6

WORKDIR /app

RUN pip install poetry==0.12.10

ADD pyproject.toml .

RUN poetry config settings.virtualenvs.in-project true \
  && poetry install

COPY model_3 model_3

CMD poetry run python model_3/extract_data.py
