from flask import render_template
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Invoice, Customer, Payment
from . import dashboard_bp

@dashboard_bp.route('/')
@dashboard_bp.route('/index')
@login_required
def index():
    """Dashboard main page"""
    today = datetime.utcnow().date()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Statistics
    total_customers = Customer.query.count()
    total_invoices = Invoice.query.count()
    
    # Monthly data
    monthly_invoices = Invoice.query.filter(
        func.date(Invoice.date) >= first_day,
        func.date(Invoice.date) <= last_day
    ).count()
    
    monthly_payments = db.session.query(func.sum(Payment.amount)).filter(
        func.date(Payment.payment_date) >= first_day,
        func.date(Payment.payment_date) <= last_day
    ).scalar() or 0
    
    # Unpaid invoices
    unpaid_invoices = Invoice.query.filter(
        Invoice.status.in_(['unpaid', 'partial'])
    ).count()
    
    unpaid_invoices_data = Invoice.query.filter(
        Invoice.status.in_(['unpaid', 'partial'])
    ).all()
    
    total_unpaid = sum(inv.remaining_amount for inv in unpaid_invoices_data)
    
    # Overdue invoices
    overdue_invoices = Invoice.query.filter(
        Invoice.due_date < today,
        Invoice.status.in_(['unpaid', 'partial'])
    ).count()
    
    # Recent data
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    
    data = {
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'monthly_invoices': monthly_invoices,
        'monthly_payments': float(monthly_payments),
        'unpaid_invoices': unpaid_invoices,
        'total_unpaid': total_unpaid,
        'overdue_invoices': overdue_invoices,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments
    }
    
    return render_template('dashboard/index.html', data=data)