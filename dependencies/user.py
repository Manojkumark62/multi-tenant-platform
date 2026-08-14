from fastapi import Depends
from models.user import User
from dependencies.auth import get_current_user

def get_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user