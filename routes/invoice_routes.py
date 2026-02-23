from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Invoice, Customer, Payment
from datetime import datetime, timedelta
from . import invoice_bp
from .auth_routes import admin_required
import uuid

def generate_invoice_number():
    """Generate unique invoice number"""
    date_str = datetime.now().strftime('%Y%m%d')
    unique_str = str(uuid.uuid4())[:8].upper()
    return f'INV-{date_str}-{unique_str}'

@invoice_bp.route('/', methods=['GET'])
@login_required
def list_invoices():
    """Display all invoices"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    customer_id = request.args.get('customer_id', '', type=int)
    
    query = Invoice.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page,
        per_page=10
    )
    
    customers = Customer.query.all()
    
    return render_template(
        'invoice/list.html',
        invoices=invoices,
        customers=customers,
        status_filter=status_filter,
        customer_id=customer_id
    )

@invoice_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_invoice():
    """Create new invoice"""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        description = request.form.get('description')
        amount = request.form.get('amount', type=float)
        due_date_str = request.form.get('due_date')
        
        # Validation
        if not all([customer_id, amount, due_date_str]):
            flash('Customer ID, Nominal, dan Jatuh Tempo harus diisi.', 'warning')
            return redirect(url_for('invoice.create_invoice'))
        
        if amount <= 0:
            flash('Nominal harus lebih dari 0.', 'warning')
            return redirect(url_for('invoice.create_invoice'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
            invoice = Invoice(
                invoice_number=generate_invoice_number(),
                customer_id=customer_id,
                date=datetime.utcnow(),
                due_date=due_date,
                description=description,
                amount=amount,
                status='unpaid'
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            flash(f'Tagihan {invoice.invoice_number} berhasil dibuat.', 'success')
            return redirect(url_for('invoice.list_invoices'))
        except ValueError:
            flash('Format tanggal tidak valid.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    customers = Customer.query.filter_by(status='active').all()
    return render_template('invoice/create.html', customers=customers)

@invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@login_required
def view_invoice(invoice_id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(invoice_id)
    payments = Payment.query.filter_by(invoice_id=invoice_id).all()
    
    return render_template(
        'invoice/view.html',
        invoice=invoice,
        payments=payments
    )

@invoice_bp.route('/edit/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_invoice(invoice_id):
    """Edit invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check if invoice has been partially paid
    if invoice.paid_amount > 0:
        flash('Tidak dapat mengedit tagihan yang sudah ada pembayaran.', 'warning')
        return redirect(url_for('invoice.view_invoice', invoice_id=invoice_id))
    
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount', type=float)
        due_date_str = request.form.get('due_date')
        
        if not all([amount, due_date_str]):
            flash('Nominal dan Jatuh Tempo harus diisi.', 'warning')
            return redirect(url_for('invoice.edit_invoice', invoice_id=invoice_id))
        
        if amount <= 0:
            flash('Nominal harus lebih dari 0.', 'warning')
            return redirect(url_for('invoice.edit_invoice', invoice_id=invoice_id))
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
            invoice.description = description
            invoice.amount = amount
            invoice.due_date = due_date
            
            db.session.commit()
            flash('Tagihan berhasil diubah.', 'success')
            return redirect(url_for('invoice.view_invoice', invoice_id=invoice_id))
        except ValueError:
            flash('Format tanggal tidak valid.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('invoice/edit.html', invoice=invoice)

@invoice_bp.route('/delete/<int:invoice_id>', methods=['POST'])
@login_required
@admin_required
def delete_invoice(invoice_id):
    """Delete invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check if invoice has payments
    if invoice.payments:
        flash('Tidak dapat menghapus tagihan yang sudah ada pembayaran.', 'warning')
        return redirect(url_for('invoice.view_invoice', invoice_id=invoice_id))
    
    try:
        invoice_number = invoice.invoice_number
        db.session.delete(invoice)
        db.session.commit()
        flash(f'Tagihan {invoice_number} berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('invoice.list_invoices'))

@invoice_bp.route('/api/by-customer/<int:customer_id>')
@login_required
def get_customer_invoices(customer_id):
    """Get unpaid invoices for a customer"""
    invoices = Invoice.query.filter(
        Invoice.customer_id == customer_id,
        Invoice.status != 'paid'
    ).all()
    
    return jsonify([{
        'id': inv.id,
        'invoice_number': inv.invoice_number,
        'amount': inv.amount,
        'paid_amount': inv.paid_amount,
        'remaining_amount': inv.remaining_amount,
        'status': inv.status
    } for inv in invoices])