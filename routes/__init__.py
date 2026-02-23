from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
customer_bp = Blueprint('customer', __name__, url_prefix='/customers')
invoice_bp = Blueprint('invoice', __name__, url_prefix='/invoices')
payment_bp = Blueprint('payment', __name__, url_prefix='/payments')
report_bp = Blueprint('report', __name__, url_prefix='/report')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Import routes to register them
from . import auth_routes
from . import customer_routes
from . import invoice_routes
from . import payment_routes
from . import report_routes
from . import dashboard_routes

def init_routes(app):
    """Register all blueprints with the app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(dashboard_bp)