# add_vendor.py
from app import app, db, Vendor

with app.app_context():
    v = Vendor(name="Test Vendor", username="testvendor", password="test123")
    db.session.add(v)
    db.session.commit()
    print("✅ Sample vendor added.")
