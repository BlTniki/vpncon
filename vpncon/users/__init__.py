from flask import Blueprint

from .service import UserService, UserServiceCRUD

user_service: UserService = UserServiceCRUD()

users_bp = Blueprint('users_api', __name__, url_prefix='/users')

from .api import *
# users package
