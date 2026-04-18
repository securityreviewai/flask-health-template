from __future__ import annotations

from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def save_patient_clinic_file(
    store_root: Path,
    patient_id: int,
    file: FileStorage,
) -> Path:
    """Persist a multipart upload under ``store_root/<patient_id>/``.

    The stored name is the uploader-supplied filename (basename only), passed through
    ``secure_filename`` so path components and unsafe characters cannot escape the
    patient directory.
    """
    if not file.filename:
        msg = "Uploaded file must include a filename"
        raise ValueError(msg)

    root = store_root.resolve()
    original_basename = Path(file.filename).name
    stored_name = secure_filename(original_basename)
    if not stored_name:
        msg = "Invalid filename after sanitization"
        raise ValueError(msg)

    patient_dir = (root / str(patient_id)).resolve()
    if not patient_dir.is_relative_to(root):
        msg = "Invalid patient_id path"
        raise ValueError(msg)

    patient_dir.mkdir(parents=True, exist_ok=True)
    destination = patient_dir / stored_name
    file.save(destination)
    return destination


def save_patient_scan_upload(
    uploads_root: Path,
    patient_id: int,
    file: FileStorage,
) -> Path:
    """Persist a scan under ``uploads_root/<patient_id>/`` (see ``save_patient_clinic_file``)."""
    return save_patient_clinic_file(uploads_root, patient_id, file)
