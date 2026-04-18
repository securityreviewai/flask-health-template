import subprocess
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from app.auth import clinician_required
from app.extensions import db
from app.models import Patient, Visit
from app.pg_backup import dump_postgres_database
from app.scan_uploads import save_patient_clinic_file
from app.soap_notes import soap_notes_to_html

bp = Blueprint("main", __name__)


@bp.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@bp.get("/api/patients")
def list_patients() -> tuple:
    return jsonify({"patients": []}), 200


@bp.get("/api/patients/<int:patient_id>/profile")
def patient_profile(patient_id: int) -> tuple:
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return jsonify({"error": "patient not found"}), 404

    raw_allergies = patient.allergies
    if raw_allergies is None:
        allergy_list: list[str] = []
    elif isinstance(raw_allergies, list):
        allergy_list = [str(item) for item in raw_allergies]
    else:
        allergy_list = []

    return (
        jsonify(
            {
                "name": patient.full_name,
                "notes": patient.notes,
                "allergies": allergy_list,
            }
        ),
        200,
    )


@bp.get("/visits/<int:visit_id>/soap-notes")
def visit_soap_notes(visit_id: int) -> str:
    visit = db.session.get(Visit, visit_id)
    if visit is None:
        abort(404)
    soap_html = soap_notes_to_html(visit.soap_notes)
    return render_template(
        "clinical/visit_soap.html",
        visit=visit,
        soap_html=soap_html,
    )


@bp.get("/reports/<filename>")
@clinician_required
def download_lab_report(filename: str):
    """Serve a lab report PDF from disk for a logged-in clinician (see ``clinician_required``)."""
    safe_name = secure_filename(filename)
    if not safe_name or not safe_name.lower().endswith(".pdf"):
        abort(400)

    reports_root = Path(current_app.config["LAB_REPORTS_DIR"]).resolve()
    file_path = (reports_root / safe_name).resolve()
    if not file_path.is_file() or not file_path.is_relative_to(reports_root):
        abort(404)

    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=safe_name,
    )


@bp.post("/api/patients/<int:patient_id>/scans")
def upload_patient_scan(patient_id: int) -> tuple:
    """Accept a multipart scan file (field name ``scan``) and store it on disk."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return jsonify({"error": "patient not found"}), 404

    upload = request.files.get("scan")
    if upload is None:
        return jsonify({"error": "multipart form must include a scan file"}), 400

    uploads_root = Path(current_app.config["CLINIC_UPLOADS_DIR"])
    try:
        saved_path = save_patient_clinic_file(uploads_root, patient_id, upload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return (
        jsonify(
            {
                "patient_id": patient_id,
                "path": str(saved_path),
                "filename": saved_path.name,
            }
        ),
        201,
    )


@bp.post("/api/patients/<int:patient_id>/documents")
def upload_patient_document(patient_id: int) -> tuple:
    """Store patient-provided documents (insurance card, ID, referral, etc.) on disk."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return jsonify({"error": "patient not found"}), 404

    upload = request.files.get("document")
    if upload is None:
        return jsonify({"error": "multipart form must include a document file"}), 400

    documents_root = Path(current_app.config["CLINIC_DOCUMENTS_DIR"])
    try:
        saved_path = save_patient_clinic_file(documents_root, patient_id, upload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return (
        jsonify(
            {
                "patient_id": patient_id,
                "path": str(saved_path),
            }
        ),
        201,
    )


@bp.post("/admin/pg-dump")
def admin_pg_dump() -> tuple:
    """POST form field ``database_name``; run ``pg_dump`` and save under ``CLINIC_BACKUP_DIR``."""
    database_name = (request.form.get("database_name") or "").strip()
    if not database_name:
        return jsonify({"error": "database_name is required"}), 400

    backup_root = Path(current_app.config["CLINIC_BACKUP_DIR"])
    pg_dump_bin = current_app.config.get("PG_DUMP_BIN", "pg_dump")

    try:
        dump_path = dump_postgres_database(
            database_name,
            sqlalchemy_database_uri=current_app.config["SQLALCHEMY_DATABASE_URI"],
            backup_root=backup_root,
            pg_dump_bin=pg_dump_bin,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"error": "pg_dump executable not found"}), 500
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
        return jsonify({"error": "pg_dump failed", "detail": err}), 500

    return jsonify({"path": str(dump_path)}), 201
