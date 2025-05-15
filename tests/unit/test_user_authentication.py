from werkzeug.security import generate_password_hash, check_password_hash

def test_password_check():
    password = "abc123"
    hashed = generate_password_hash(password)
    assert check_password_hash(hashed, password)
    assert not check_password_hash(hashed, "wrongpass")
