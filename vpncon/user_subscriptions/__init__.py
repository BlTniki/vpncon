from flask import Blueprint

from .service import UserSubscriptionService, UserSubscriptionServiceCRUD

user_subscription_service: UserSubscriptionService = UserSubscriptionServiceCRUD()

user_subscriptions_bp = Blueprint('user_subscriptions_api', __name__, url_prefix='/user-subscriptions')

from .api import *
# user_subscriptions package