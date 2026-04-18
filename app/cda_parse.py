from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

# HL7 CDA R2 uses the HL7 Version 3 XML namespace.
_HL7_V3 = "{urn:hl7-org:v3}"
# ICD-10-CM in HL7 OID registry
_ICD10_CM_OID = "2.16.840.1.113883.6.90"


def _local(tag: str) -> str:
    return f"{_HL7_V3}{tag}"


def _extract_patient_name(root: ET.Element) -> str:
    for patient in root.iter(_local("patient")):
        for name_el in patient.findall(_local("name")):
            given = [
                t
                for g in name_el.findall(_local("given"))
                if (t := (g.text or "").strip())
            ]
            family = [
                t
                for f in name_el.findall(_local("family"))
                if (t := (f.text or "").strip())
            ]
            parts = [*given, *family]
            if parts:
                return " ".join(parts)
    return ""


def _collect_icd10_codes(root: ET.Element) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def add(code: str | None) -> None:
        if code and code not in seen:
            seen.add(code)
            ordered.append(code)

    for el in root.iter(_local("code")):
        if el.get("codeSystem") == _ICD10_CM_OID:
            add(el.get("code"))

    # Coded values on observations (xsi:type="CD") often carry the diagnosis code.
    for el in root.iter(_local("value")):
        if el.get("codeSystem") == _ICD10_CM_OID:
            add(el.get("code"))

    return ordered


def parse_cda_document(xml_bytes: bytes | str) -> dict[str, Any]:
    """Parse CDA XML and return patient display name plus ICD-10-CM diagnosis codes.

    ``xml_bytes`` may be UTF-8 ``bytes`` or a string (interpreted as UTF-8 when encoded).

    Patient name is taken from the first ``recordTarget`` / ``patientRole`` / ``patient``
    ``name`` with ``given`` / ``family`` children. Diagnosis codes are ``@code`` values
    on ``code`` or ``value`` elements whose ``@codeSystem`` is the ICD-10-CM OID
    (``2.16.840.1.113883.6.90``).
    """
    raw = xml_bytes.encode("utf-8") if isinstance(xml_bytes, str) else xml_bytes
    root = ET.fromstring(raw)

    return {
        "patient_name": _extract_patient_name(root),
        "diagnosis_codes": _collect_icd10_codes(root),
    }
