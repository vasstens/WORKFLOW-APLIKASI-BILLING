from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Customer
from . import customer_bp
from .auth_routes import admin_required

@customer_bp.route('/', methods=['GET'])
@login_required
def list_customers():
    """Display all customers"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        )
    
    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page,
        per_page=10
    )
    
    return render_template(
        'customer/list.html',
        customers=customers,
        search=search
    )

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_customer():
    """Add new customer"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        
        # Validation
        if not all([name, phone, email]):
            flash('Nama, HP, dan Email harus diisi.', 'warning')
            return redirect(url_for('customer.add_customer'))
        
        if Customer.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'warning')
            return redirect(url_for('customer.add_customer'))
        
        # Create new customer
        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            status='active'
        )
        
        try:
            db.session.add(customer)
            db.session.commit()
            flash(f'Pelanggan {name} berhasil ditambahkan.', 'success')
            return redirect(url_for('customer.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('customer/add.html')

@customer_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_customer(customer_id):
    """Edit customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        status = request.form.get('status', 'active')
        
        # Validation
        if not all([name, phone, email]):
            flash('Nama, HP, dan Email harus diisi.', 'warning')
            return redirect(url_for('customer.edit_customer', customer_id=customer_id))
        
        # Check if email is already used by another customer
        existing = Customer.query.filter(
            Customer.email == email,
            Customer.id != customer_id
        ).first()
        
        if existing:
            flash('Email sudah digunakan pelanggan lain.', 'warning')
            return redirect(url_for('customer.edit_customer', customer_id=customer_id))
        
        try:
            customer.name = name
            customer.phone = phone
            customer.email = email
            customer.address = address
            customer.status = status
            
            db.session.commit()
            flash(f'Pelanggan {name} berhasil diubah.', 'success')
            return redirect(url_for('customer.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('customer/edit.html', customer=customer)

@customer_bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
@admin_required
def delete_customer(customer_id):
    """Delete customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        # Check if customer has unpaid invoices
        from models import Invoice
        unpaid_invoices = Invoice.query.filter(
            Invoice.customer_id == customer_id,
            Invoice.status != 'paid'
        ).first()
        
        if unpaid_invoices:
            flash('Tidak dapat menghapus pelanggan yang memiliki tagihan belum lunas.', 'warning')
            return redirect(url_for('customer.list_customers'))
        
        db.session.delete(customer)
        db.session.commit()
        flash(f'Pelanggan {customer.name} berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('customer.list_customers'))

@customer_bp.route('/api/<int:customer_id>')
@login_required
def get_customer(customer_id):
    """Get customer data as JSON"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address
    })