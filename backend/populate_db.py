from sqlalchemy import create_engine, text
import requests
import json

# PostgreSQL database
engine = create_engine("postgresql://postgres:Trishaal1$@localhost/pokemon_db", echo=True)

# Function to fetch Pokémon data from API
def fetch_pokemon(id_or_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{id_or_name}"
    response = requests.get(url)
    data = response.json()
    
    # Try to get animated sprite, fall back to static
    animated_image = None
    try:
        animated_image = data['sprites']['versions']['generation-v']['black-white']['animated']['front_default']
    except (KeyError, TypeError):
        pass
    
    return {
        'pokedex_number': data['id'],
        'name': data['name'],
        'weight': data['weight'],
        'height': data['height'],
        'image': data['sprites']['front_default'],
        'animated_image': animated_image,
        'stats': json.dumps(data['stats'])
    }

# Initialize DB
print("Setting up database...")
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS pokemon"))
    conn.execute(text("""
        CREATE TABLE pokemon (
            id SERIAL PRIMARY KEY,
            pokedex_number INTEGER UNIQUE,
            name TEXT UNIQUE,
            weight INTEGER,
            height INTEGER,
            image TEXT,            animated_image TEXT,            stats TEXT
        )
    """))

# Fetch all 1025 Pokémon
print("Fetching Pokémon data... This may take several minutes.")
for i in range(1, 1026):  # IDs 1-1025
    try:
        p = fetch_pokemon(i)
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO pokemon (pokedex_number, name, weight, height, image, animated_image, stats) VALUES (:pokedex_number, :name, :weight, :height, :image, :animated_image, :stats) ON CONFLICT (name) DO NOTHING"), p)
        if i % 50 == 0:
            print(f"Loaded {i} Pokémon...")
    except Exception as e:
        print(f"Error fetching Pokémon {i}: {e}")

print("All Pokémon loaded!")

# Show final count
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM pokemon"))
    count = result.scalar()
    print(f"Database now contains {count} Pokémon")
