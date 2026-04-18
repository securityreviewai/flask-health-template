from datetime import datetime

from app.extensions import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)


class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="scheduled")
    soap_notes = db.Column(db.Text, nullable=True)
