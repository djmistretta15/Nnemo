from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, data: RegisterRequest) -> dict:
        """
        Register a new organization and admin user.
        
        Returns:
            Dict with access_token and refresh_token
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == data.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if organization already exists
        existing_org = self.db.query(Organization).filter(
            Organization.name == data.organization_name
        ).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name already taken"
            )
        
        # Create organization
        organization = Organization(
            name=data.organization_name,
            description=f"Organization for {data.organization_name}"
        )
        self.db.add(organization)
        self.db.flush()
        
        # Create admin user
        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role="org_admin",
            organization_id=organization.id
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def login_user(self, data: LoginRequest) -> dict:
        """
        Authenticate user and return tokens.
        
        Returns:
            Dict with access_token and refresh_token
        """
        user = self.db.query(User).filter(User.email == data.email.lower()).first()
        
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
