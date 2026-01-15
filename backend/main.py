from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pathlib import Path
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL database
engine = create_engine("postgresql://postgres:Trishaal1$@localhost/pokemon_db", echo=True)

@app.get("/pokemon")
def get_pokemon(sort_by: str = "id", limit: int = 100):
    # Parse and calculate stats for each Pokemon
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, pokedex_number, name, weight, height, image, animated_image, stats FROM pokemon"))
        pokemon_list = []
        
        for row in result:
            pokemon = dict(row._mapping)
            stats_data = json.loads(pokemon['stats'])
            
            # Extract individual stats
            stats_dict = {}
            total_stats = 0
            for stat in stats_data:
                stat_name = stat['stat']['name']
                stat_value = stat['base_stat']
                stats_dict[stat_name] = stat_value
                total_stats += stat_value
            
            pokemon['parsed_stats'] = stats_dict
            pokemon['total_stats'] = total_stats
            pokemon_list.append(pokemon)
        
        # Sort based on the sort_by parameter
        if sort_by == "height":
            pokemon_list.sort(key=lambda x: x['height'], reverse=True)
        elif sort_by == "weight":
            pokemon_list.sort(key=lambda x: x['weight'], reverse=True)
        elif sort_by == "total_stats":
            pokemon_list.sort(key=lambda x: x['total_stats'], reverse=True)
        elif sort_by == "total_stats_low":
            pokemon_list.sort(key=lambda x: x['total_stats'])
        elif sort_by in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]:
            pokemon_list.sort(key=lambda x: x['parsed_stats'].get(sort_by, 0), reverse=True)
        elif sort_by.endswith("_low") and sort_by.replace("_low", "") in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]:
            stat_name = sort_by.replace("_low", "")
            pokemon_list.sort(key=lambda x: x['parsed_stats'].get(stat_name, 0))
        else:
            # Default sort by id
            pokemon_list.sort(key=lambda x: x['id'])
        
        # Limit results
        return pokemon_list[:limit]

# Path to frontend folder
frontend_path = Path(__file__).parent.parent / "frontend"

# Serve HTML at root
@app.get("/")
def root():
    return FileResponse(frontend_path / "index.html")

# Serve static files (CSS, JS, images) - must be after route definitions
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
