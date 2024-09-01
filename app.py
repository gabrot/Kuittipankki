from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import os
from forms import LoginForm, RegisterForm, ReceiptForm, CategoryForm, TagForm, PaymentMethodForm, VendorForm, DateRangeForm
import models
from models import User, get_vendors, create_vendor
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the database connection
try:
    models.init_db()
    logger.info("Database connection initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database connection: {e}")
    raise

@login_manager.user_loader
def load_user(user_id):
    return models.get_user_by_id(int(user_id))

@app.route('/')
def root():
    logger.info(f"Accessing root route. User session: {session}")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    logger.info(f"Accessing index route for user_id: {current_user.id}")
    receipts = models.get_user_receipts(current_user.id)
    return render_template('index.html', receipts=receipts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Accessing login route")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = models.get_user_by_username(form.username.data)
        if user and check_password_hash(user['password'], form.password.data):
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            logger.info(f"User {user['id']} logged in successfully")
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt for username: {form.username.data}")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.id} logged out")
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    logger.info("Accessing register route")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user_id = models.create_user(form.username.data, hashed_password)
        if user_id:
            flash('Registration successful! You can now log in.', 'success')
            logger.info(f"New user registered with id: {user_id}")
            return redirect(url_for('login'))
        flash('Username already exists.', 'error')
        logger.warning(f"Registration failed: Username {form.username.data} already exists")
    return render_template('register.html', form=form)

@app.route('/profile')
@login_required
def profile():
    logger.info(f"Accessing profile route for user_id: {current_user.id}")
    user = models.get_user_by_id(current_user.id)
    return render_template('profile.html', user=user)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = ReceiptForm()
    form.category.choices = [(c['id'], c['name']) for c in models.get_categories()]
    form.payment_method.choices = [(pm['id'], pm['name']) for pm in models.get_payment_methods()]
    form.tags.choices = [(t['id'], t['name']) for t in models.get_tags()]
    form.vendor.choices = [(v['id'], v['name']) for v in models.get_vendors()]

    if form.validate_on_submit():
        try:
            filename = secure_filename(form.file.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(filepath)
            
            receipt_id = models.create_receipt(
                filename, 
                form.description.data, 
                form.amount.data, 
                form.receipt_date.data, 
                current_user.id, 
                form.category.data,
                form.vendor.data, 
                form.payment_method.data
            )
            
            if receipt_id:
                models.add_receipt_tags(receipt_id, form.tags.data)
                flash('Receipt uploaded successfully!', 'success')
                return redirect(url_for('index'))
            else:
                raise Exception("Receipt creation failed")
        except Exception as e:
            app.logger.error(f"Error uploading receipt: {str(e)}")
            flash(f'Error uploading receipt: {str(e)}', 'error')
    else:
        app.logger.warning(f"Form validation failed: {form.errors}")
    
    return render_template('upload.html', form=form)

@app.route('/view_receipt/<int:receipt_id>')
@login_required
def view_receipt(receipt_id):
    logger.info(f"Accessing view_receipt route for receipt_id: {receipt_id}")
    receipt = models.get_receipt_by_id(receipt_id)
    if receipt and receipt['user_id'] == current_user.id:
        tags = models.get_receipt_tags(receipt_id)
        return render_template('view_receipt.html', receipt=receipt, tags=tags)
    logger.warning(f"Unauthorized access attempt to receipt_id: {receipt_id} by user_id: {current_user.id}")
    abort(404)

@app.route('/edit_receipt/<int:receipt_id>', methods=['GET', 'POST'])
@login_required
def edit_receipt(receipt_id):
    logger.info(f"Accessing edit_receipt route for receipt_id: {receipt_id}")
    receipt = models.get_receipt_by_id(receipt_id)
    if not receipt or receipt['user_id'] != current_user.id:
        logger.warning(f"Unauthorized edit attempt for receipt_id: {receipt_id} by user_id: {current_user.id}")
        abort(404)

    form = ReceiptForm(obj=receipt)
    form.category.choices = [(c['id'], c['name']) for c in models.get_categories()]
    form.vendor.choices = [(v['id'], v['name']) for v in models.get_vendors()]
    form.payment_method.choices = [(pm['id'], pm['name']) for pm in models.get_payment_methods()]
    form.tags.choices = [(t['id'], t['name']) for t in models.get_tags()]

    if form.validate_on_submit():
        models.update_receipt(
            receipt_id, form.description.data, form.amount.data,
            form.receipt_date.data, form.category.data,
            form.vendor.data, form.payment_method.data
        )
        models.update_receipt_tags(receipt_id, form.tags.data)
        flash('Receipt updated successfully!', 'success')
        logger.info(f"Receipt {receipt_id} updated successfully by user_id: {current_user.id}")
        return redirect(url_for('view_receipt', receipt_id=receipt_id))

    return render_template('edit_receipt.html', form=form, receipt=receipt)

@app.route('/delete_receipt/<int:receipt_id>', methods=['POST'])
@login_required
def delete_receipt(receipt_id):
    logger.info(f"Accessing delete_receipt route for receipt_id: {receipt_id}")
    receipt = models.get_receipt_by_id(receipt_id)
    if receipt and receipt['user_id'] == current_user.id:
        if models.delete_receipt(receipt_id):
            flash('Receipt deleted successfully.', 'success')
            logger.info(f"Receipt {receipt_id} deleted successfully by user_id: {current_user.id}")
        else:
            flash('Error deleting receipt.', 'error')
            logger.error(f"Error deleting receipt {receipt_id} for user_id: {current_user.id}")
    else:
        logger.warning(f"Unauthorized delete attempt for receipt_id: {receipt_id} by user_id: {current_user.id}")
        abort(404)
    return redirect(url_for('index'))

@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    category_form = CategoryForm()
    tag_form = TagForm()
    payment_method_form = PaymentMethodForm()
    vendor_form = VendorForm()

    if request.method == 'POST':
        if 'add_category' in request.form and category_form.validate_on_submit():
            models.create_category(category_form.name.data, category_form.description.data)
            flash('Category added successfully', 'success')
        elif 'add_tag' in request.form and tag_form.validate_on_submit():
            models.create_tag(tag_form.name.data)
            flash('Tag added successfully', 'success')
        elif 'add_payment_method' in request.form and payment_method_form.validate_on_submit():
            models.create_payment_method(payment_method_form.name.data, payment_method_form.description.data)
            flash('Payment method added successfully', 'success')
        elif 'delete_category' in request.form:
            category_id = request.form['delete_category']
            models.delete_category(category_id)
            flash('Category deleted successfully', 'success')
        elif 'add_vendor' in request.form and vendor_form.validate_on_submit():
            models.create_vendor(vendor_form.name.data, vendor_form.address.data, vendor_form.phone.data)
            flash('Vendor added successfully', 'success')
        elif 'delete_tag' in request.form:
            tag_id = request.form['delete_tag']
            models.delete_tag(tag_id)
            flash('Tag deleted successfully', 'success')
        elif 'delete_payment_method' in request.form:
            payment_method_id = request.form['delete_payment_method']
            models.delete_payment_method(payment_method_id)
            flash('Payment method deleted successfully', 'success')
        elif 'delete_vendor' in request.form:
            vendor_id = request.form['delete_vendor']
            models.delete_vendor(vendor_id)
            flash('Vendor deleted successfully', 'success')
        return redirect(url_for('manage'))
    
    categories = models.get_categories()
    tags = models.get_tags()
    payment_methods = models.get_payment_methods()
    vendors = models.get_vendors()

    return render_template('manage.html', 
                           category_form=category_form,
                           tag_form=tag_form,
                           payment_method_form=payment_method_form,
                           vendor_form=vendor_form,
                           categories=categories,
                           tags=tags,
                           payment_methods=payment_methods,
                           vendors=vendors)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = DateRangeForm()
    spending_by_category = None
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        try:
            spending_by_category = models.get_spending_by_category(current_user.id, start_date, end_date)
        except Exception as e:
            flash(f"An error occurred while fetching the report: {str(e)}", "error")
            app.logger.error(f"Error in reports route: {str(e)}")
    
    return render_template('reports.html', form=form, spending_by_category=spending_by_category)

@app.route('/spending_by_category', methods=['GET', 'POST'])
@login_required
def spending_by_category():
    logger.info(f"Accessing spending_by_category route for user_id: {current_user.id}")
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        spending = models.get_user_spending_by_category(current_user.id, start_date, end_date)
        return render_template('spending_report.html', spending=spending, report_type='category')
    return render_template('report_form.html', report_type='category')

@app.route('/spending_by_vendor', methods=['GET', 'POST'])
@login_required
def spending_by_vendor():
    logger.info(f"Accessing spending_by_vendor route for user_id: {current_user.id}")
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        spending = models.get_user_spending_by_vendor(current_user.id, start_date, end_date)
        return render_template('spending_report.html', spending=spending, report_type='vendor')
    return render_template('report_form.html', report_type='vendor')

@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False)