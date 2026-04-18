from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from flask import current_app, render_template
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Patient


def generate_patient_pdf(patient_id: int, output_name: str) -> Path:
    """Render an HTML patient summary and convert it to a PDF with ``wkhtmltopdf``.

    The PDF is written under ``CLINIC_PATIENT_PDF_DIR`` using a sanitized
    ``output_name`` (must end in ``.pdf``; ``.pdf`` is appended if missing).

    Requires a Flask application context. Raises ``FileNotFoundError`` if
    ``wkhtmltopdf`` is not on ``PATH`` (or ``WKHTMLTOPDF_BIN``), and
    ``subprocess.CalledProcessError`` if conversion fails.
    """
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        msg = f"patient not found: {patient_id}"
        raise ValueError(msg)

    raw_allergies = patient.allergies
    if isinstance(raw_allergies, list):
        allergies = [str(x) for x in raw_allergies]
    else:
        allergies = []

    html = render_template(
        "reports/patient_pdf_summary.html",
        patient=patient,
        allergies=allergies,
    )

    safe_name = secure_filename(output_name)
    if not safe_name:
        msg = "output_name must yield a non-empty filename after sanitization"
        raise ValueError(msg)
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"

    pdf_root = Path(current_app.config["CLINIC_PATIENT_PDF_DIR"]).resolve()
    pdf_root.mkdir(parents=True, exist_ok=True)
    output_path = (pdf_root / safe_name).resolve()
    if not output_path.is_relative_to(pdf_root):
        msg = "refusing output path outside CLINIC_PATIENT_PDF_DIR"
        raise ValueError(msg)

    wkhtml = os.environ.get("WKHTMLTOPDF_BIN", "wkhtmltopdf")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        delete=False,
        encoding="utf-8",
    ) as tmp_html:
        tmp_html.write(html)
        html_path = tmp_html.name

    try:
        subprocess.run(
            [wkhtml, "--quiet", html_path, str(output_path)],
            check=True,
            capture_output=True,
            timeout=120,
        )
    finally:
        Path(html_path).unlink(missing_ok=True)

    return output_path
