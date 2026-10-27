from __future__ import annotations

import numbers
from dataclasses import asdict, dataclass, field
from typing import Any

from exceptions import ValidationError


@dataclass
class Subject:
    subject_id: int
    subject_title: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Semester:
    semster_id: int
    semster_title: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StudentSubject:
    student_subject_id: int
    subject: Subject
    mark: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StudentSemester:
    student_semester_id: int
    semester: Semester
    student_subjects: list[StudentSubject] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Student:
    student_id: int
    firstname: str
    lastname: str
    student_semesters: list[StudentSemester] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


MAX_TITLE_LENGTH = 255


def validate_string(raw: Any):
    if not isinstance(raw, str):
        raise ValidationError("title must be a string")
    title = raw.strip()
    if not title:
        raise ValidationError("title must not be empty")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f"title must be at most {MAX_TITLE_LENGTH} characters")
    return title


def validate_mark(raw: Any):
    if not isinstance(raw, numbers.Number):
        raise ValidationError(f"Mark has to be a number, {raw} is not valid")
    if raw < 1:
        raise ValidationError("Mark has to be larger or equal to 1")
    if raw > 6:
        raise ValidationError("Mark is not allowed to be larger than 6")
    return raw


def get_student_semester(student: Student, semester: Semester):
    for student_semester in student.student_semesters:
        if student_semester.semester.semster_id == semester.semster_id:
            return student_semester
    return None


def get_subject_of_student(student: Student, subject: Subject):
    for student_stemester in student.student_semesters:
        for student_subject in student_stemester.student_subjects:
            if student_subject.subject_id == subject.subject_id:
                return student_subject
    return None


def get_subject_of_student_of_semester(student: Student, semester: Semester, subject: Subject):
    student_semester = get_student_semester(student, semester)
    if student_semester:
        for student_subject in student_semester.student_subjects:
            if student_subject.subject.subject_id == subject.subject_id:
                return student_subject
    return None


def check_subject_in_use(students: list[Student], subject_id):
    for student in students:
        for student_semester in student.student_semesters:
            for student_subject in student_semester.student_subjects:
                if student_subject.subject.subject_id == subject_id:
                    return True

    return False


def check_studened_already_passed_subject(student: Student, subject: Subject):
    student_subject = get_subject_of_student(student, subject)
    return student_subject and student_subject.mark >= 4.0
