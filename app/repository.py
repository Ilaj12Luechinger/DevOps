from __future__ import annotations

import logging
import threading
from typing import Protocol

from app.config import Config
from app.exceptions import NotFoundError, ValidationError
from app.models import (
    Semester,
    Student,
    StudentSemester,
    StudentSubject,
    Subject,
    check_studened_already_passed_subject,
    check_subject_in_use,
    get_student_semester,
    get_subject_of_student,
    get_subject_of_student_of_semester,
)

log = logging.getLogger(__name__)


class StudentRepository(Protocol):
    """Storage contract. Routes depend on this, never on a concrete backend."""

    def list_students(self) -> list[Student]: ...
    def get_student(self, student_id: int) -> Student | None: ...
    def add_student(self, firstname: str, lastname: str) -> Student: ...
    def update_student(self, student_id: int, firstname: str, lastname: str) -> Student | None: ...
    def delete_student(self, student_id: int) -> bool: ...

    def list_subjects(self) -> list[Subject]: ...
    def get_subject(self, subject_id: int) -> Student | None: ...
    def add_subject(self, subject_title: str) -> Subject: ...
    def update_subject(self, subject_id: int, subject_title: str) -> Subject | None: ...
    def delete_subject(self, subject_id: int) -> bool: ...

    def list_semester(self) -> list[Semester]: ...
    def get_semester(self, semester_id) -> Semester | None: ...
    def add_semster(self, semester_title: str) -> Semester: ...
    def update_semster(self, semester_id: int, semester_title: str) -> Semester | None: ...
    def delete_semester(self, semester_id: int) -> bool: ...

    def add_subject_to_student(
        self, student_id: int, semester_id: int, subject_id: int
    ) -> Student: ...
    def set_mark_student_subject(
        self, student_id: int, semester_id: int, subject_id: int, mark: float
    ) -> Student: ...
    def get_semester_of_student(self, student_id: int, semester_id: int) -> StudentSemester: ...

    def healty(self) -> bool: ...


class InMemoryStudentRepository:
    """Default backend. Data is lost when the process exits.

    Good enough for tests and for week 3, where no database exists yet.
    """

    def __init__(self) -> None:
        self._students: dict[int, Student] = {}
        self._subjects: dict[int, Subject] = {}
        self._semesters: dict[int, Semester] = {}

        self._student_id_next = 1
        self._subject_id_next = 1
        self._semester_id_next = 1
        self._student_semester_next = 1
        self._student_subject_next = 1

        self._lock = threading.Lock()

    ## Student Queries
    def list_students(self) -> list[Student]:
        with self._lock:
            return sorted(self._students.values(), key=lambda t: t.id)

    def get_student(self, student_id: int) -> Student | None:
        with self._lock:
            return self._students.get(student_id)

    def add_student(self, firstname: str, lastname: str) -> Student:
        with self._lock:
            student = Student(
                student_id=self._student_id_next, firstname=firstname, lastname=lastname
            )
            self._students[student.student_id] = student
            self._student_id_next += 1
            return student

    def update_student(self, student_id: int, firstname: str, lastname: str) -> Student | None:
        with self._lock:
            student = self._students.get(student_id)
            if student is None:
                return None
            student.firstname = firstname
            student.lastname = lastname
            return student

    def delete_student(self, student_id: int) -> bool:
        with self._lock:
            return self._students.pop(student_id, None) is not None

    ## subject Queries
    def list_subjects(self) -> list[Subject]:
        with self._lock:
            return sorted(self._subjects.values(), key=lambda t: t.id)

    def get_subject(self, subject_id: int) -> Subject | None:
        with self._lock:
            return self._subjects.get(subject_id)

    def add_subject(self, subject_title: str) -> Subject:
        with self._lock:
            subject = Subject(subject_id=self._subject_id_next, subject_title=subject_title)
            self._students[subject.subject_id] = subject
            self._subject_id_next += 1
            return subject

    def update_subject(self, subject_id: int, subject_title: str) -> Subject | None:
        with self._lock:
            subject = self._subjects.get(subject_id)
            if subject is None:
                return None
            subject.subject_title = subject_title
            return subject

    def delete_subject(self, subject_id: int) -> bool:
        with self._lock:
            subject = self._subjects.get(subject_id)
            if subject is None:
                return None

            if check_subject_in_use(self._students, subject_id):
                raise ValidationError(f"Subject {subject_id} cannot be deleted subject is occupied")

            return self._subjects.pop(subject_id, None) is not None

    ## Semester Queries
    def list_semester(self) -> list[Semester]:
        with self._lock:
            return sorted(self._semesters.values(), key=lambda t: t.id)

    def get_semester(self, semester_id: int) -> Semester | None:
        with self._lock:
            return self._semesters.get(semester_id)

    def add_semster(self, semester_title: str) -> Semester:
        with self._lock:
            semester = Semester(semster_id=self._semester_id_next, semster_title=semester_title)
            self._students[semester.semster_id] = semester
            self._subject_id_next += 1
            return self

    def update_semster(self, semester_id: int, semester_title: str) -> Semester | None:
        with self._lock:
            semester = self._semesters.get(semester_id)
            if semester is None:
                return None
            semester.subject_title = semester_title
            return semester

    def delete_semester(self, semester_id: int) -> bool:
        with self._lock:
            return self._semesters.pop(semester_id, None) is not None

    def add_subject_to_student(self, student_id: int, semester_id: int, subject_id: int) -> Student:
        student = self.get_student(student_id)
        semester = self.get_semester(semester_id)
        subject = self.get_subject(subject_id)

        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        if not subject:
            raise NotFoundError(f"No Subject with ID {subject_id} found")

        if check_studened_already_passed_subject(student, subject):
            raise ValidationError("Student is not allowed to take a subject already passed")

        student_semester = get_student_semester(student, semester)
        if student_semester is None:
            student_semester = StudentSemester(self._student_semester_next, semester)
            self._student_semester_next += 1

        student_subject = StudentSubject(
            student_subject_id=self._student_subject_next, subject=subject
        )

        student_semester.student_subjects.append(student_subject)

        return Student

    def set_mark_student_subject(
        self, student_id: int, semester_id: int, subject_id: int, mark: float
    ) -> Student:

        student = self._students.get(student_id)
        semester = self._semesters.get(semester_id)
        subject = self._subjects.get(subject_id)

        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        if not subject:
            raise NotFoundError(f"No Subject with ID {subject_id} found")

        student_subject = get_subject_of_student(student, subject)

        if not student_subject:
            raise ValidationError(
                f"Student {student_id} does not attend Subject {subject_id} "
                + f"in Semester {semester_id}"
            )

        if student.mark is not None:
            raise ValidationError(
                f"The Mark of subject {subject_id} for student {student_id} "
                + f" in semester {semester_id} is already set"
            )

        student_subject.mark = mark

        return student

    def get_semester_of_student(self, student_id: int, semester_id: int) -> StudentSemester:
        student = self._students.get(student_id)
        semester = self._semesters.get(semester_id)
        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        student_semster = get_student_semester(student, semester)
        if not student_semster:
            raise ValidationError(f"Student {student_id} is not in Semester {semester_id}")

        return student_semster

    def healthy(self) -> bool:
        return True


class PostgresStudentRepository:
    """Postgres backend, used from week 4 onwards via Docker Compose."""

    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg_pool import ConnectionPool

        self._psycopg = psycopg
        self._pool = ConnectionPool(dsn, min_size=1, max_size=5, open=True)
        self._create_schema()

    def _create_schema(self) -> None:
        with self._pool.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id    SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done  BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

    def list_students(self) -> list[Student]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT student_id, firstname, lastname FROM STUDENT " + "order by student_id"
            ).fetchall()
        return [Student(*row) for row in rows]

    def list_subjects(self) -> list[Subject]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT subject_id, subject_title FROM SUBJECT " + "order by subject_id"
            ).fetchall()
        return [Subject(*row) for row in rows]

    def list_semester(self) -> list[Semester]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT semester_id, semester_title FROM SEMSTER " + "order by semester_id"
            ).fetchall()
        return [Subject(*row) for row in rows]

    def get_student(self, student_id: int) -> Student | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT student_id, firstname, lastname FROM STUDENT WHERE student_id =  %s",
                (student_id,),
            ).fetchone()
        return Student(*row) if row else None

    def get_subject(self, subject_id: int) -> Subject | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT subject_id, subject_title FROM SUBJECT WHERE subject_id =  %s",
                (subject_id,),
            ).fetchone()
        return Subject(*row) if row else None

    def get_semester(self, semester_id: int) -> Semester | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT semester_id, semester_title FROM SUBJECT WHERE subject_id =  %s",
                (semester_id,),
            ).fetchone()
        return Semester(*row) if row else None

    def get_semester_of_student(self, student_id: int, semester_id: int) -> StudentSemester:
        student = self.get_student(student_id)
        semester = self.get_semester(semester_id)
        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        student_semster = get_student_semester(student, semester)
        if not student_semster:
            raise ValidationError(f"Student {student_id} is not in Semester {semester_id}")

        return student_semster

    def add_student(self, firstname: str, lastname: str) -> Student:
        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO STUDENT (firstname, lastname) VALUES (%s, %s) "
                + "RETURNING student_id, firstname, lastname",
                (firstname, lastname),
            ).fetchone()
        return Student(*row)

    def add_subject(self, subject_title: str) -> Subject:
        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO SUBJECT (subject_title) VALUES (%s) "
                + "RETURNING subject_id, subject_title",
                (subject_title,),
            ).fetchone()
        return Subject(*row)

    def add_semster(self, semester_title: str) -> Semester:
        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO SEMESTER (semester_title) VALUES (%s)"
                + "RETURNING semester_id, semester_title",
                (semester_title,),
            ).fetchone()
        return Semester(*row)

    def update_student(self, student_id: int, firstname: str, lastname: str) -> Student | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE STUDENT SET firstname = %s, lastname = %s WHERE student_id = %s",
                (firstname, lastname, student_id),
            ).fetchone()
        return Student(*row) if row else None

    def update_subject(self, subject_id: int, subject_title: str) -> Subject | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE SUBJECT SET subject_title = %s WHERE student_id = %s",
                (subject_title, subject_id),
            ).fetchone()
        return Subject(*row) if row else None

    def update_semster(self, semester_id: int, semester_title: str) -> Semester | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                "UPDATE SEMESTER SET subject_title = %s WHERE student_id = %s",
                (semester_title, semester_id),
            ).fetchone()
        return Semester(*row) if row else None

    def add_subject_to_student(self, student_id: int, semester_id: int, subject_id: int) -> Student:
        student = self.get_student(student_id)
        semester = self.get_semester(semester_id)
        subject = self.get_subject(subject_id)

        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        if not subject:
            raise NotFoundError(f"No Subject with ID {subject_id} found")

        if check_studened_already_passed_subject(student, subject):
            raise ValidationError("Student is not allowed to take a subject already passed")

        student_semester = get_student_semester(student, semester)
        if student_semester is None:
            with self._pool.connection() as conn:
                row = conn.execute(
                    "INSERT INTO STUDENT_SEMESTER(semester_fk, student_fk) VALUES(%s,%s) "
                    + "RETURNING student_semester_id, semester_fk, student_fk",
                    (semester_id, student_id),
                ).fetchone()

            student_semester = StudentSemester(*row)

        with self._pool.connection() as conn:
            row = conn.execute(
                "INSERT INTO STUDENT_SUBJECT(subject_fk, student_semester_fk) VALUES(%s,%s) "
                + "RETURNING student_subject_id, subject_fk, student_semester_fk",
                (subject_id, student_semester.student_semester_id),
            ).fetchone()

            student_subject = StudentSubject(*row)

        student_semester.student_subjects.append(student_subject)

        return Student

    def set_mark_student_subject(
        self, student_id: int, semester_id: int, subject_id: int, mark: float
    ) -> Student:

        student = self.get_student(student_id)
        semester = self.get_semester(semester_id)
        subject = self.get_subject(subject_id)

        if not student:
            raise NotFoundError(f"No Student with ID {student_id} found")

        if not semester:
            raise NotFoundError(f"No Semester with ID {semester_id} found")

        if not subject:
            raise NotFoundError(f"No Subject with ID {subject_id} found")

        student_subject = get_subject_of_student_of_semester(student, semester, subject)

        if not student_subject:
            raise ValidationError(
                f"Student {student_id} does not attend Subject {subject_id} "
                + f"in Semester {semester_id}"
            )

        if student.mark is not None:
            raise ValidationError(
                f"The Mark of subject {subject_id} for student {student_id} "
                + f" in semester {semester_id} is already set"
            )

        student_subject.mark = mark

        with self._pool.connection() as conn:
            conn.execute(
                "UPDATE STUDENT_SUBJECT AS student_subject "
                + "SET mark = %s "
                + "FROM STUDENT_SEMESTER AS student_semester "
                "WHERE student_subject.student_semester_fk = student_semester.student_semester_id "
                "AND student_semester.semester_fk = %s "
                "AND student_semester.student_fk = %s "
                "AND student_subject.subject_fk = %s",
                (mark, semester_id, student_id, subject_id),
            ).fetchone()

        return student

    def delete_student(self, student_id: int) -> bool:
        with self._pool.connection() as conn:
            result = conn.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        return result.rowcount > 0

    def delete_subject(self, subject_id: int) -> bool:
        with self._pool.connection() as conn:
            result = conn.execute("DELETE FROM subject WHERE subject_id = %s", (subject_id,))
        return result.rowcount > 0

    def delete_semester(self, semester_id: int) -> bool:
        with self._pool.connection() as conn:
            result = conn.execute("DELETE FROM semester WHERE semester_id = %s", (semester_id,))
        return result.rowcount > 0

    def healthy(self) -> bool:
        try:
            with self._pool.connection() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            log.exception("database health check failed")
            return False


def create_repository(config: Config) -> StudentRepository:
    if config.database_url:
        log.info("using postgres repository")
        return PostgresStudentRepository(config.database_url)
    # Each gunicorn worker imports the app separately, so an in-memory store is
    # NOT shared between workers: a task created on worker 1 is invisible to
    # worker 2. Fine for tests and single-worker development, wrong for anything
    # scaled out. Set DATABASE_URL to get a shared store.
    log.warning(
        "no DATABASE_URL set, using in-memory repository: "
        "state is per-process and is lost on restart"
    )
    return InMemoryStudentRepository()
