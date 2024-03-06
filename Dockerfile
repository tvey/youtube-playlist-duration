FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install --no-cache-dir pipenv
COPY Pipfile* ./
RUN pipenv requirements > requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . ./

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
