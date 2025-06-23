from app import db, app

REQUIRED_TABLES = {'vendor', 'customer', 'item', 'bill', 'bill_item'}

with app.app_context():
    inspector = db.inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    missing_tables = REQUIRED_TABLES - existing_tables
    extra_tables = existing_tables - REQUIRED_TABLES

    print(f"\n✅ Existing Tables: {existing_tables}")

    if missing_tables:
        print(f"❌ Missing Tables: {missing_tables}")
    else:
        print("✅ All required tables exist!")

    if extra_tables:
        print(f"⚠️  Extra Tables in DB (not required): {extra_tables}")
