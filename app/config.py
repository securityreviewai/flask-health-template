import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/health",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST", "localhost")
    OPENSEARCH_PORT = int(os.environ.get("OPENSEARCH_PORT", "9200"))
    OPENSEARCH_USER = os.environ.get("OPENSEARCH_USER", "admin")
    OPENSEARCH_PASSWORD = os.environ.get("OPENSEARCH_PASSWORD", "admin")
