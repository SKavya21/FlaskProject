from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# --- Models ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price_per_kg = db.Column(db.Float, nullable=False)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pending')

# --- Filters ---
@app.template_filter('lookup_item_name')
def lookup_item_name(item_id):
    item = Item.query.get(item_id)
    return item.name if item else "Unknown"

# --- Routes ---
@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('stock'))
    elif 'customer_id' in session:
        return redirect(url_for('vendors'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == 'vendor':
            user = Vendor.query.filter_by(username=username, password=password).first()
            if user:
                session['vendor_id'] = user.id
                return redirect(url_for('stock'))
        elif user_type == 'customer':
            user = Customer.query.filter_by(username=username, password=password).first()
            if user:
                session['customer_id'] = user.id
                return redirect(url_for('vendors'))

        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        contact = request.form.get('contact', '')

        if user_type == 'vendor':
            user = Vendor(name=name, username=username, password=password)
        else:
            user = Customer(name=name, contact=contact, username=username, password=password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        quantity = float(request.form['quantity'])
        price = float(request.form['price'])
        item = Item(name=name, quantity=quantity, price_per_kg=price)
        db.session.add(item)
        db.session.commit()

    items = Item.query.all()
    return render_template('stock.html', items=items)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        username = name.lower().replace(" ", "") + contact
        password = 'default123'
        customer = Customer(name=name, contact=contact, username=username, password=password)
        db.session.add(customer)
        db.session.commit()

    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/vendors')
def vendors():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@app.route('/request_items', methods=['GET', 'POST'])
def request_items():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_ids = request.form.getlist('item_ids')
        quantities = request.form.getlist('quantities')

        for item_id, qty in zip(item_ids, quantities):
            if qty and float(qty) > 0:
                new_request = Request(customer_id=session['customer_id'], item_id=int(item_id), quantity=float(qty))
                db.session.add(new_request)

        db.session.commit()
        flash('Item requests submitted successfully!', 'success')
        return redirect(url_for('vendors'))

    items = Item.query.all()
    return render_template('request_items.html', items=items)

@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        request_id = int(request.form['request_id'])
        action = request.form['action']

        req = Request.query.get_or_404(request_id)
        if action == 'approve':
            req.status = 'Approved'
        elif action == 'complete':
            req.status = 'Completed'
        db.session.commit()

    requests = db.session.query(Request, Customer, Item).join(Customer, Request.customer_id == Customer.id).join(Item, Request.item_id == Item.id).order_by(Request.timestamp.desc()).all()
    return render_template('view_requests.html', requests=requests)

@app.route('/my_requests')
def my_requests():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    my_requests = db.session.query(Request, Item).join(Item, Request.item_id == Item.id).filter(Request.customer_id == session['customer_id']).order_by(Request.timestamp.desc()).all()
    return render_template('my_requests.html', requests=my_requests)


@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_id = int(request.form['customer'])
        selected_items = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')

        total = 0
        bill_items = []

        for item_id, qty_str in zip(selected_items, quantities):
            qty = float(qty_str)
            item = Item.query.get(int(item_id))
            if item and 0 < qty <= item.quantity:
                subtotal = qty * item.price_per_kg
                total += subtotal
                item.quantity -= qty
                bill_items.append((item.id, qty, subtotal))

        if bill_items:
            bill = Bill(customer_id=customer_id, vendor_id=session['vendor_id'], total_amount=total)
            db.session.add(bill)
            db.session.flush()

            for item_id, qty, subtotal in bill_items:
                db.session.add(BillItem(bill_id=bill.id, item_id=item_id, quantity=qty, subtotal=subtotal))

            db.session.commit()
            return redirect(url_for('bill_detail', bill_id=bill.id))

    customers = Customer.query.all()
    items = Item.query.all()
    return render_template('generate_bill.html', customers=customers, items=items)

@app.route('/bill/<int:bill_id>')
def bill_detail(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    customer = Customer.query.get(bill.customer_id)
    vendor = Vendor.query.get(bill.vendor_id)
    bill_items = BillItem.query.filter_by(bill_id=bill.id).all()
    return render_template('bill.html', bill=bill, customer=customer, vendor=vendor, bill_items=bill_items)

@app.route('/bill_pdf/<int:bill_id>')
def bill_pdf(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    customer = Customer.query.get(bill.customer_id)
    vendor = Vendor.query.get(bill.vendor_id)
    bill_items = BillItem.query.filter_by(bill_id=bill.id).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Ration Management Bill", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"Vendor: {vendor.name}", ln=True)
    pdf.cell(200, 8, txt=f"Customer: {customer.name} | Contact: {customer.contact}", ln=True)
    pdf.cell(200, 8, txt=f"Date: {bill.date.strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(70, 10, "Item", 1)
    pdf.cell(30, 10, "Rate (INR/kg)", 1)
    pdf.cell(30, 10, "Quantity", 1)
    pdf.cell(40, 10, "Subtotal (INR)", 1)
    pdf.ln()

    pdf.set_font("Arial", '', 11)
    for item in bill_items:
        item_data = Item.query.get(item.item_id)
        pdf.cell(70, 10, item_data.name, 1)
        pdf.cell(30, 10, f"{item_data.price_per_kg:.2f}", 1)
        pdf.cell(30, 10, f"{item.quantity:.2f}", 1)
        pdf.cell(40, 10, f"{item.subtotal:.2f}", 1)
        pdf.ln()

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 10, "Total", 1)
    pdf.cell(40, 10, f"{bill.total_amount:.2f} INR", 1)

    # Convert PDF to BytesIO using dest='S'
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # avoids Unicode errors
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name=f"bill_{bill.id}.pdf", mimetype='application/pdf')

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    quantity = float(request.form['quantity'])
    price = float(request.form['price'])
    item = Item(name=name, quantity=quantity, price_per_kg=price)
    db.session.add(item)
    db.session.commit()
    flash('Item added successfully.', 'success')
    return redirect(url_for('stock'))

@app.route('/my_bills')
def my_bills():
    if 'customer_id' not in session:
        return redirect(url_for('login'))

    bills = Bill.query.filter_by(customer_id=session['customer_id']).all()
    return render_template('my_bills.html', bills=bills)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
