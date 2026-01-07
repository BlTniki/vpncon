from flask import Blueprint

from .service import HostService, HostServiceCRUD

host_service: HostService = HostServiceCRUD()

hosts_bp = Blueprint('hosts_api', __name__, url_prefix='/hosts')

from .api import *
# hosts package
