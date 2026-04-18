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

    OPENSEARCH_CLINICIAN_SESSION_INDEX = os.environ.get(
        "OPENSEARCH_CLINICIAN_SESSION_INDEX",
        "clinician_sessions",
    )

    LAB_REPORTS_DIR = os.environ.get("LAB_REPORTS_DIR", "/var/clinic/reports")
    CLINIC_UPLOADS_DIR = os.environ.get("CLINIC_UPLOADS_DIR", "/var/clinic/uploads")
    CLINIC_DOCUMENTS_DIR = os.environ.get("CLINIC_DOCUMENTS_DIR", "/var/clinic/documents")

    # Outbound webhook target (set in admin / environment for production).
    PHARMACY_CALLBACK_URL = os.environ.get("PHARMACY_CALLBACK_URL", "")

    CLINIC_PATIENT_PDF_DIR = os.environ.get("CLINIC_PATIENT_PDF_DIR", "/var/clinic/patient_pdfs")

    CLINIC_BACKUP_DIR = os.environ.get("CLINIC_BACKUP_DIR", "/var/clinic/backups")
