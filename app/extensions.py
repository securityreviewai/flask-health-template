from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from opensearchpy import OpenSearch

db = SQLAlchemy()
migrate = Migrate()


class OpenSearchClient:
    def __init__(self) -> None:
        self.client: OpenSearch | None = None

    def init_app(self, app: Flask) -> None:
        self.client = OpenSearch(
            hosts=[{"host": app.config["OPENSEARCH_HOST"], "port": app.config["OPENSEARCH_PORT"]}],
            http_auth=(app.config["OPENSEARCH_USER"], app.config["OPENSEARCH_PASSWORD"]),
            use_ssl=False,
            verify_certs=False,
        )
        app.extensions["opensearch"] = self.client


opensearch = OpenSearchClient()
