import sqlite3
import pytest
from src.crud import add_student, get_all_students, get_student_by_roll, update_student, delete_student


def test_add_student(conn):
    student_id = add_student(conn, "22CSAI001", "Riya Sharma", "CSE-AI", 2027, cgpa=8.7)
    assert student_id is not None
    students = get_all_students(conn)
    assert len(students) == 1
    assert students[0][2] == "Riya Sharma"  # name column


def test_get_student_by_roll(conn):
    add_student(conn, "22CSAI002", "Arjun Mehta", "CSE-AI", 2027, cgpa=9.1)
    student = get_student_by_roll(conn, "22CSAI002")
    assert student is not None
    assert student[1] == "22CSAI002"


def test_update_student(conn):
    student_id = add_student(conn, "22CSAI003", "Kabir Singh", "CSE-AI", 2027, cgpa=7.5)
    update_student(conn, student_id, cgpa=8.0)
    updated = get_student_by_roll(conn, "22CSAI003")
    assert updated[5] == 8.0  # cgpa column


def test_delete_student(conn):
    student_id = add_student(conn, "22CSAI004", "Sana Iqbal", "CSE-AI", 2027)
    delete_student(conn, student_id)
    assert get_student_by_roll(conn, "22CSAI004") is None


def test_duplicate_roll_number_rejected(conn):
    add_student(conn, "22CSAI005", "Dev Patel", "CSE-AI", 2027)
    with pytest.raises(sqlite3.IntegrityError):
        add_student(conn, "22CSAI005", "Another Person", "CSE-AI", 2027)