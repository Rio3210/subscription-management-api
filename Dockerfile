# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Set all required environment variables
ENV FLASK_APP=run.py \
    FLASK_ENV=development \
    DATABASE_URL=sqlite:///app.db \
    SECRET_KEY=dev-secret-key \
    JWT_SECRET_KEY=dev-jwt-secret-key \
    SQLALCHEMY_DATABASE_URI=sqlite:///app.db

# Create SQLite database directory
RUN mkdir -p instance && \
    touch instance/app.db

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]