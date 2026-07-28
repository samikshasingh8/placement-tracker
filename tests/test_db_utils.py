from src.db_utils import get_connection


def test_get_connection_enables_foreign_keys():
    conn = get_connection(":memory:")
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1
    conn.close()


def test_get_connection_uses_default_path_when_none_given(tmp_path, monkeypatch):
    import src.db_utils as db_utils
    fake_path = tmp_path / "test_default.db"
    monkeypatch.setattr(db_utils, "DB_PATH", fake_path)

    conn = get_connection()  # no path passed -> should fall back to DB_PATH
    assert fake_path.exists()
    conn.close()