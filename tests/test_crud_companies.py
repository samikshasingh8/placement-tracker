import pytest
from src.crud import add_company, get_all_companies, get_company_by_name, update_company, delete_company


def test_add_company(conn):
    company_id = add_company(conn, "TCS", sector="IT Services")
    assert company_id is not None
    assert len(get_all_companies(conn)) == 1


def test_get_company_by_name(conn):
    add_company(conn, "Amazon", sector="Product/E-commerce")
    company = get_company_by_name(conn, "Amazon")
    assert company[1] == "Amazon"


def test_update_company(conn):
    company_id = add_company(conn, "Infosys")
    update_company(conn, company_id, sector="IT Services")
    company = get_company_by_name(conn, "Infosys")
    assert company[2] == "IT Services"


def test_delete_company(conn):
    company_id = add_company(conn, "TempCo")
    delete_company(conn, company_id)
    assert get_company_by_name(conn, "TempCo") is None


def test_duplicate_company_name_rejected(conn):
    import sqlite3
    add_company(conn, "Wipro")
    with pytest.raises(sqlite3.IntegrityError):
        add_company(conn, "Wipro")
        
def test_update_company_with_no_fields_is_a_no_op(conn):
    company_id = add_company(conn, "NoChangeCo", sector="IT Services")
    update_company(conn, company_id)  # deliberately no keyword args
    company = get_company_by_name(conn, "NoChangeCo")
    assert company[2] == "IT Services"