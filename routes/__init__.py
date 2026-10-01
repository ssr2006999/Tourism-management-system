from flask import Blueprint

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
booking_bp = Blueprint('booking', __name__)
admin_bp = Blueprint('admin', __name__)

import routes.main
import routes.auth
import routes.booking
import routes.admin