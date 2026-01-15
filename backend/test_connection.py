from sqlalchemy import create_engine, text

# Try connecting to default postgres database first
engine = create_engine("postgresql://postgres:Trishaal1$@localhost/postgres", echo=True)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connection to PostgreSQL server successful!")
        print("PostgreSQL version:", result.fetchone()[0])
        
        # Now check if pokemon_db exists
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datname = 'pokemon_db'"))
        if result.fetchone():
            print("Database 'pokemon_db' exists.")
        else:
            print("Database 'pokemon_db' does not exist.")
except Exception as e:
    print("Connection failed:", str(e))