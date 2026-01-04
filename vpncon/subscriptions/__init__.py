from flask import Blueprint

from .service import SubscriptionService, SubscriptionServiceCRUD

subscription_service: SubscriptionService = SubscriptionServiceCRUD()

subscriptions_bp = Blueprint('subscriptions_api', __name__, url_prefix='/subscriptions')

from .api import *
# subscriptions package
