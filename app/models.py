from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


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
