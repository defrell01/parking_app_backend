from sqlalchemy import create_engine, inspect

engine = create_engine('sqlite:///../bookings.sqlite', connect_args={'check_same_thread': False})
inspector = inspect(engine)
tables = inspector.get_table_names()

print("Tables in the database:")
for table in tables:
    print(table)