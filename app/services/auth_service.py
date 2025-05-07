from typing import Tuple, Optional
import bcrypt
from flask_jwt_extended import create_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.database import db


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def _hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _check_password(self, password: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def register_user(self, email: str, password: str) -> Tuple[User, str]:
        # Check if user already exists
        if self.user_repository.get_by_email(email):
            raise ValueError("Email already registered")

        password_hash = self._hash_password(password)
        user = self.user_repository.create(email, password_hash)
        access_token = create_access_token(identity=str(user.id))
        
        return user, access_token

    def login_user(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        user = self.user_repository.get_by_email(email)
        
        if not user or not self._check_password(password, user.password_hash):
            return None, None

        access_token = create_access_token(identity=str(user.id))
        return user, access_token

    def authenticate_user(self, email, password):
        user = self.user_repository.get_by_email(email)
        if not user or not self._check_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        return user

    def get_user_by_id(self, user_id):
        return self.user_repository.get_by_id(user_id)

    def update_user(self, user_id, **kwargs):
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if 'password' in kwargs:
            kwargs['password_hash'] = self._hash_password(kwargs.pop('password'))

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user 