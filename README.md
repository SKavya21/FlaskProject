
# 🧾 Ration Management System

A web-based application for managing ration distribution using **Flask**, **SQLAlchemy**, **Bootstrap**, and **FPDF**.  
This app supports **vendor** and **customer** roles, allows for **stock management**, **customer registration**, **item requests**, **billing**, and **PDF invoice generation**.

---

## 🚀 Features

- Vendor & Customer authentication system
- Vendor-side item stock management
- Customer-side item request system
- Admin-approved request handling (approve/complete)
- Bill generation with real-time stock update
- PDF generation of detailed bills using FPDF
- Responsive frontend using HTML, CSS, and Bootstrap
- SQLite database for data persistence

---

## 🧰 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite via SQLAlchemy ORM
- **Frontend**: HTML + Bootstrap + CSS
- **PDF Generation**: FPDF (Python)

---

## 📂 Project Structure

```
/ration-management/
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── stock.html
│   ├── customers.html
│   ├── vendors.html
│   ├── request_items.html
│   ├── view_requests.html
│   ├── my_requests.html
│   ├── generate_bill.html
│   ├── bill.html
│   ├── my_bills.html
├── static/
│   ├── css/
│   └── js/
├── app.py
├── requirements.txt
├── README.md
```

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/SKavya21/FlaskProject.git
cd ration-management
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🛠️ Usage

### 1. Initialize the database
```bash
python app.py
```

This will create `ration.db` in your project directory.

### 2. Run the app
```bash
python app.py
```
Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔐 Default Credentials

You can register a new vendor or customer using the registration page.

Default customer password: `default123` (if created by a vendor).

---

## 📄 Generate PDF Bills

- After generating a bill, click **"Download PDF"** to get a printable receipt with all itemized details.

---

## 📋 Dependencies (`requirements.txt`)

```txt
Flask==3.0.2
Flask-SQLAlchemy==3.1.1
fpdf==1.7.2
```

Install them with:
```bash
pip install -r requirements.txt
```

---

## ✅ To Do (Optional Enhancements)

- Add Flask-Login for secure session management
- Add password hashing (e.g., with `werkzeug.security`)
- Implement search/filtering on items/customers
- Add billing history exports (CSV, Excel)
- Role-based access control (admin, vendor, customer)

---

## 📸 Screenshots
You can add screenshots in this section (optional).

---

## 👨‍💻 Author

- Soneji Kavya
- GitHub: https://github.com/SKavya21/SKavya21.git
