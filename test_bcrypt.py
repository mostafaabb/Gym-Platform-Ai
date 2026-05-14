from passlib.context import CryptContext
import bcrypt

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    h = pwd_context.hash("test")
    print(f"Passlib hash: {h}")
    print(f"Passlib verify: {pwd_context.verify('test', h)}")
except Exception as e:
    print(f"Passlib error: {e}")

try:
    salt = bcrypt.gensalt()
    h = bcrypt.hashpw(b"test", salt)
    print(f"Bcrypt hash: {h}")
    print(f"Bcrypt verify: {bcrypt.checkpw(b"test", h)}")
except Exception as e:
    print(f"Bcrypt error: {e}")
