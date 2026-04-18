from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

# FHIR R4 XML namespace for resources in a typical Bundle.
_FHIR = "http://hl7.org/fhir"
_LOINC = "http://loinc.org"


def _tag(ns_uri: str, local: str) -> str:
    return f"{{{ns_uri}}}{local}"


def _primitive_value(parent: ET.Element, ns_uri: str, local: str) -> str | None:
    el = parent.find(_tag(ns_uri, local))
    if el is None:
        return None
    return el.get("value")


def _extract_namespace_uri(elem: ET.Element) -> str:
    if elem.tag.startswith("{"):
        return elem.tag[1 : elem.tag.index("}")]
    return _FHIR


def _parse_patients(root: ET.Element, ns_uri: str) -> dict[str, dict[str, Any]]:
    """Map logical id (resource id) -> minimal patient fields."""
    patients: dict[str, dict[str, Any]] = {}
    for patient in root.iter(_tag(ns_uri, "Patient")):
        pid = _primitive_value(patient, ns_uri, "id")
        if not pid:
            continue
        name_parts: list[str] = []
        for nm in patient.findall(_tag(ns_uri, "name")):
            for g in nm.findall(_tag(ns_uri, "given")):
                v = g.get("value") or (g.text or "").strip()
                if v:
                    name_parts.append(v.strip())
            fam = nm.find(_tag(ns_uri, "family"))
            if fam is not None:
                v = fam.get("value") or (fam.text or "").strip()
                if v:
                    name_parts.append(v.strip())
        patients[pid] = {
            "resource_type": "Patient",
            "id": pid,
            "name": " ".join(name_parts).strip() or None,
        }
    return patients


def _codeable_concept_summary(code_el: ET.Element | None, ns_uri: str) -> dict[str, str | None]:
    if code_el is None:
        return {"text": None, "system": None, "code": None, "display": None}

    out: dict[str, str | None] = {
        "text": _primitive_value(code_el, ns_uri, "text"),
        "system": None,
        "code": None,
        "display": None,
    }
    for coding in code_el.findall(_tag(ns_uri, "coding")):
        sys = _primitive_value(coding, ns_uri, "system")
        code = _primitive_value(coding, ns_uri, "code")
        disp = _primitive_value(coding, ns_uri, "display")
        if sys or code or disp:
            out["system"] = sys
            out["code"] = code
            out["display"] = disp
            break
    return out


def _observation_value(obs: ET.Element, ns_uri: str) -> dict[str, Any]:
    """Normalize common lab value shapes."""
    if (vq := obs.find(_tag(ns_uri, "valueQuantity"))) is not None:
        return {
            "kind": "quantity",
            "value": _primitive_value(vq, ns_uri, "value"),
            "unit": _primitive_value(vq, ns_uri, "unit"),
            "system": _primitive_value(vq, ns_uri, "system"),
        }
    if (vs := obs.find(_tag(ns_uri, "valueString"))) is not None:
        v = vs.get("value")
        if v is None and vs.text:
            v = vs.text.strip()
        return {"kind": "string", "value": v}
    if (vc := obs.find(_tag(ns_uri, "valueCodeableConcept"))) is not None:
        summary = _codeable_concept_summary(vc, ns_uri)
        return {"kind": "codeable_concept", **summary}
    return {"kind": None}


def _parse_observations(
    root: ET.Element,
    ns_uri: str,
    patients: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for obs in root.iter(_tag(ns_uri, "Observation")):
        oid = _primitive_value(obs, ns_uri, "id")
        status = _primitive_value(obs, ns_uri, "status")
        effective = _primitive_value(obs, ns_uri, "effectiveDateTime")
        if effective is None and (ed := obs.find(_tag(ns_uri, "effectivePeriod"))) is not None:
            effective = _primitive_value(ed, ns_uri, "start")

        code_el = obs.find(_tag(ns_uri, "code"))
        code_info = _codeable_concept_summary(code_el, ns_uri)

        subject_ref = None
        if (subj := obs.find(_tag(ns_uri, "subject"))) is not None:
            subject_ref = _primitive_value(subj, ns_uri, "reference")

        patient_id = None
        patient_name = None
        if subject_ref:
            # "Patient/123" or full URL ending with Patient/123
            if "/" in subject_ref:
                patient_id = subject_ref.rsplit("/", 1)[-1]
                pinfo = patients.get(patient_id)
                if pinfo:
                    patient_name = pinfo.get("name")

        value_info = _observation_value(obs, ns_uri)

        results.append(
            {
                "observation_id": oid,
                "status": status,
                "effective_datetime": effective,
                "patient_reference": subject_ref,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "code_text": code_info.get("text"),
                "code_system": code_info.get("system"),
                "code": code_info.get("code"),
                "code_display": code_info.get("display"),
                "is_loinc": code_info.get("system") == _LOINC,
                "value": value_info,
            }
        )
    return results


def parse_fhir_lab_bundle_xml(xml_bytes: bytes | str) -> list[dict[str, Any]]:
    """Parse a FHIR XML Bundle (or fragment) containing Patient and Observation resources.

    Returns one dict per ``Observation`` (lab result), with coded name, timing, value,
    and patient linkage when ``subject.reference`` matches a ``Patient.id`` in the same
    document.

    ``xml_bytes`` may be UTF-8 bytes or a Unicode string (encoded as UTF-8).
    """
    raw = xml_bytes.encode("utf-8") if isinstance(xml_bytes, str) else xml_bytes
    root = ET.fromstring(raw)
    ns_uri = _extract_namespace_uri(root)

    patients = _parse_patients(root, ns_uri)
    return _parse_observations(root, ns_uri, patients)
