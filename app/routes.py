from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

from app.models import (
    validate_string,
    validate_mark
    )
from app.exceptions import (
    NotFoundError,
    ValidationError
)

bp = Blueprint("main", __name__)


def _repo():
    return current_app.extensions["repository"]


def _config():
    return current_app.extensions["app_config"]


@bp.errorhandler(ValidationError)
def _handle_validation_error(exc: ValidationError):
    return jsonify(error=str(exc)), 400

@bp.errorhandler(NotFoundError)
def _handle_not_found_error(exc: NotFoundError):
    return jsonify(error=str(exc)), 204


@bp.get("/")
def index():
    return render_template("index.html", version=_config().version)


@bp.get("/health")
def health():
    """Liveness: is the process up? Must not touch the database.

    Kubernetes restarts the container when this fails, so a slow database
    must never be able to trigger a restart loop.
    """
    return jsonify(status="ok", version=_config().version)


@bp.get("/ready")
def ready():
    """Readiness: can this instance serve traffic? Checks dependencies."""
    if _repo().healthy():
        return jsonify(status="ready")
    return jsonify(status="unavailable"), 503


@bp.get("/api/students")
def list_students():
    return jsonify([t.to_dict() for t in _repo().list_students()])

@bp.get("/api/subjects")
def list_subjects():
    return jsonify([t.to_dict() for t in _repo().list_subjects()])

@bp.get("/api/semesters")
def list_semesters():
    return jsonify([t.to_dict() for t in _repo().list_semesters()])

@bp.get("/api/students/<int:student_id>")
def get_student(student_id: int):
    student = _repo().get_student(student_id)
    if student is None:
        return jsonify(error="Student not found"), 404
    return jsonify(student.to_dict())


@bp.get("/api/subjects")
def get_subject(subject_id: int):
    subject = _repo().get_subject(subject_id)
    if subject is None:
        return jsonify(error="Subject not found"), 404
    return jsonify(subject.to_dict())

@bp.get("/api/semesters/<int:semester_id>")
def get_semesters(semester_id: int):
    semester = _repo().get_subject(semester_id)
    if semester is None:
        return jsonify(error="Semester not found"), 404
    return jsonify(semester.to_dict())


@bp.get("/api/students/<int:student_id>/semesters")
def get_semesters_of_student(student_id: int):
    return jsonify(_repo().get_semesters_of_student(student_id))


@bp.get("/api/students/<int:student_id>/semesters/<int:semester_id>")
def get_semester_of_student(student_id: int, semester_id: int):
    return jsonify(_repo().get_semester_of_student(student_id, semester_id))


@bp.get("/api/students/<int:student_id>/semesters/<int:student_semester_id>/subjects")
def get_subjects_of_student_semester(student_id: int, student_semester_id: int):
    return jsonify(_repo().get_subjects_of_student_semester(student_semester_id))


@bp.post("/api/students")
def create_student():
    payload = request.get_json(silent=True) or {}
    firstname = validate_string(payload.get("firstname"))
    lastname = validate_string(payload.get("lastname"))
    student = _repo().add_student(firstname, lastname)
    return jsonify(student.to_dict()), 201


@bp.post("/api/subjects")
def create_subject():
    payload = request.get_json(silent=True) or {}
    subject_title = validate_string(payload.get("subject_title"))
    subject = _repo().add_subject(subject_title)
    return jsonify(subject.to_dict()), 201


@bp.post("/api/semesters")
def create_semester():
    payload = request.get_json(silent=True) or {}
    semester_title = validate_string(payload.get("semester_title"))
    semester = _repo().add_subject(semester_title)
    return jsonify(semester.to_dict()), 201


@bp.put("/api/students/<int:student_id>")
def update_student(student_id: int):
    payload = request.get_json(silent=True) or {}
    if student_id != payload.get("student_id"):
        raise ValidationError("Student ID in Pathparam and Body do not match")
    firstname = validate_string(payload.get("firstname"))
    lastname = validate_string(payload.get("lastname"))
    student = _repo().update_student(student_id, firstname, lastname)
    return jsonify(student.to_dict())


@bp.put("/api/subjects/<int:subject_id>")
def update_subject(subject_id: int):
    payload = request.get_json(silent=True) or {}
    if subject_id != payload.get("subject_id"):
        raise ValidationError("Subject ID in Pathparam and Body do not match")
    subject_title = validate_string(payload.get("subject_title"))
    subject = _repo().update_student(subject_id, subject_title)
    return jsonify(subject.to_dict())


@bp.put("/api/semesters/<int:semester_id>")
def update_semester(semester_id: int):
    payload = request.get_json(silent=True) or {}
    if semester_id != payload.get("semester_id"):
        raise ValidationError("Semester ID in Pathparam and Body do not match")
    semester_title = validate_string(payload.get("semester_title"))

    student = _repo().update_semester(semester_id, semester_title)
    return jsonify(student.to_dict())


@bp.post("/api/students/<int:student_id>/semester/<int:semester_id>/subject/<int:subject_id>")
def add_subject_to_student(student_id: int, semster_id: int, subject_id: int):
    student = _repo().add_subject_to_student(student_id, semster_id, subject_id)
    return jsonify(student.to_dict())

@bp.put("/api/students/<int:student_id>/semester/<int:semester_id>/subject/<int:subject_id>/mark")
def set_mark_to_student(student_id: int, semster_id: int, subject_id: int):
    payload = request.get_json(silent=True) or {}
    mark = validate_mark(payload.get("mark"))
    student = _repo().set_mark_student_subject(student_id, semster_id, subject_id, mark)
    return jsonify(student.to_dict())


@bp.delete("/api/students/<int:student_id>")
def delete_student(student_id: int):
    if not _repo().delete_student(student_id):
        return jsonify(error="Student not found"), 404
    return "", 204


@bp.delete("/api/subjects/<int:subject_id>")
def delete_subject(subject_id: int):
    if not _repo().delete_student(subject_id):
        return jsonify(error="Subject not found"), 404
    return "", 204


@bp.delete("/api/subjects/<int:subject_id>")
def delete_semester(subject_id: int):
    if not _repo().delete_student(subject_id):
        return jsonify(error="Subject not found"), 404
    return "", 204

