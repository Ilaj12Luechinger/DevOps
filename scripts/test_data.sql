
-- 1. Insert Subjects
INSERT INTO SUBJECT (subject_title) VALUES 
('Mathematics'),
('Computer Science'),
('Physics'),
('English Literature');

-- 2. Insert Semesters
INSERT INTO SEMESTER (semester_title) VALUES 
('Fall 2026'),
('Spring 2027');

-- 3. Insert Students
INSERT INTO STUDENT (firstname, lastname) VALUES 
('Alice', 'Smith'),
('Bob', 'Jones'),
('Charlie', 'Brown');

-- 4. Insert Student Semesters (Linking students to semesters)
INSERT INTO STUDENT_SEMESTER (semester_fk, student_fk) VALUES 
(1, 1), -- Alice in Fall 2026
(2, 1), -- Alice in Spring 2027
(1, 2); -- Bob in Fall 2026

-- 5. Insert Student Subjects (Linking subjects to specific student semesters)
INSERT INTO STUDENT_SUBJECT (subject_fk, student_semester_fk) VALUES 
(1, 1), -- Alice takes Mathematics in Fall 2026
(2, 1), -- Alice takes Computer Science in Fall 2026
(3, 2), -- Alice takes Physics in Spring 2027
(1, 3); -- Bob takes Mathematics in Fall 2026
