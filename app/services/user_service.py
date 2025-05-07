from app.models import User
from app.core.database import db
from sqlalchemy import text

class UserService:
    def get_user_by_email(self, email):
        query = text("""
            SELECT u.id, u.email, u.is_admin, u.created_at,
                   COUNT(s.id) as subscription_count,
                   MAX(s.created_at) as last_subscription_date
            FROM users u
            LEFT JOIN subscriptions s ON u.id = s.user_id
            WHERE u.email = :email
            GROUP BY u.id, u.email, u.is_admin, u.created_at
        """)
        
        result = db.session.execute(query, {'email': email}).first()
        if result:
            return dict(result)
        return None

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def create_user(self, email, password, is_admin=False):
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")
            
        user = User(email=email, is_admin=is_admin)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user 