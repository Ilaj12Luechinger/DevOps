CREATE TABLE SUBJECT(
    subject_id SERIAL PRIMARY KEY, 
    subject_title varchar(255) NOT NULL
    );

CREATE TABLE SEMESTER(
    semester_id SERIAL PRIMARY KEY,
    semester_title varchar(255) NOT NULL
);

CREATE TABLE STUDENT (
    student_id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL
);

CREATE TABLE STUDENT_SEMESTER(
    student_semester_id SERIAL PRIMARY KEY,
    semester_fk int,
    student_fk int,
    CONSTRAINT semester_fk
    FOREIGN KEY (semester_fk)
    REFERENCES SEMESTER(semester_id),
    CONSTRAINT student_fk
    FOREIGN KEY (student_fk)
    REFERENCES STUDENT(student_id)
);

CREATE TABLE STUDENT_SUBJECT(
    student_subject_id SERIAL PRIMARY KEY,
    subject_fk int,
    student_semester_fk int,
    mark float,

    CONSTRAINT subject_fk
    FOREIGN KEY  (subject_fk)
    REFERENCES SUBJECT(subject_id),
    CONSTRAINT student_semester_fk
    FOREIGN KEY (student_semester_fk)
    REFERENCES STUDENT_SEMESTER(student_semester_id)
); 
