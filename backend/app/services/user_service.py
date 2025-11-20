from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role,
            organization_id=data.organization_id
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email.lower()).first()
