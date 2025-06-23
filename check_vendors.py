from app import app, db, Vendor

with app.app_context():
    vendors = Vendor.query.all()
    if not vendors:
        print("❌ No vendors found.")
    else:
        print("✅ Found vendors:")
        for v in vendors:
            print(f"- {v.id}: {v.name} ({v.username})")
