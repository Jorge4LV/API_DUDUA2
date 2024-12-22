import discord
from discord.ext import commands
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
import json
import asyncio
import uvicorn
import os
import random
import requests
from Config.Funciones.registrar import registrar_rutas_desde_directorio
from Config.Funciones.datos_json import load_data
from Config.Funciones.guardar_json import save_data
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = FastAPI()

discord_token = os.getenv("DISCORD_TOKEN")
guild_id = os.getenv("GUILD_ID")
application_id = os.getenv("APPLICATION_ID")


@app.get("/app-emojis-plain")
def get_app_emojis_plain():
    application_id = os.getenv("APPLICATION_ID")
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {
        "Authorization": f"Bot {discord_token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emojis = response.json().get("items", [])
        formatted_emojis = "\n".join([f"<:{emoji['name']}:{emoji['id']}>" for emoji in emojis])
        return formatted_emojis
    else:
        return "Error al obtener la lista de emojis."

@app.get("/app-emojis")
def get_app_emojis():
     
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {
        "Authorization": f"Bot {discord_token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emojis = response.json().get("items", [])
        filtered_emojis = [{"name": emoji["name"], "id": emoji["id"]} for emoji in emojis]
        
        # Guardar la información en un archivo JSON
        with open("app_emojis_data.json", "w") as file:
            json.dump(filtered_emojis, file, indent=4)
        
        return filtered_emojis  # También devuelve la información a la API
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch app emojis")

@app.get("/emojis")
def get_emojis():
    url = f"https://discord.com/api/v10/guilds/{guild_id}/emojis"
    headers = {
        "Authorization": f"Bot {discord_token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emojis = response.json()
        filtered_emojis = [{"name": emoji["name"], "id": emoji["id"]} for emoji in emojis]
        
        # Guardar la información en un archivo JSON
        with open("emojis_data.json", "w") as file:
            json.dump(filtered_emojis, file, indent=4)
        
        return filtered_emojis  # También devuelve la información a la API
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch emojis")


# Endpoint para obtener un GIF aleatorio por tipo de reacción
@app.get("/gifs/{reaction_type}")
def get_gif_by_reaction(reaction_type: str):
    """
    Devuelve un GIF aleatorio de un tipo específico de reacción.
    """
    try:
        # Cargar datos desde el archivo JSON
        with open("gifs_data.json", "r") as file:
            gifs_data = json.load(file)
        
        # Filtrar GIFs por tipo de reacción
        filtered_gifs = [gif for gif in gifs_data.get("gifs", []) if gif.get("type") == reaction_type]
        
        if not filtered_gifs:
            raise HTTPException(status_code=404, detail=f"No GIFs found for reaction type '{reaction_type}'.")
        
        # Seleccionar un GIF aleatorio de los filtrados
        random_gif = random.choice(filtered_gifs)
        return {
            "url": random_gif["url"],
            "name": random_gif["name"],
            "description": random_gif.get("description", "No description available.")
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="GIF data file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para listar los tipos de reacciones disponibles
@app.get("/gifs")
def list_gif_reaction_types():
    """
    Devuelve una lista de tipos de reacciones disponibles (endpoints únicos).
    """
    try:
        # Cargar datos desde el archivo JSON
        with open("gifs_data.json", "r") as file:
            gifs_data = json.load(file)
        
        # Extraer los tipos de reacción únicos
        reaction_types = sorted(set(gif.get("type") for gif in gifs_data.get("gifs", [])))
        
        if not reaction_types:
            raise HTTPException(status_code=404, detail="No reaction types available.")
        
        # Devolver los tipos de reacciones como endpoints
        return {
            "endpoints": [f"/gifs/{reaction}" for reaction in reaction_types]
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="GIF data file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@bot.event
async def on_raw_reaction_add(payload):
    data = load_data()
    guild = bot.get_guild(payload.guild_id)
    for role_entry in data.get("reacion", []):
        if (role_entry["channel_id"] == str(payload.channel_id) and
                role_entry["message_id"] == str(payload.message_id) and
                role_entry["emoji"] == str(payload.emoji)):
            role = guild.get_role(int(role_entry["role_id"]))
            if role:
                member = guild.get_member(payload.user_id)
                await member.add_roles(role)
                print(f"Added {role.name} to {member.name}")

@bot.event
async def on_raw_reaction_remove(payload):
    data = load_data()
    guild = bot.get_guild(payload.guild_id)
    for role_entry in data.get("reacion", []):
        if (role_entry["channel_id"] == str(payload.channel_id) and
                role_entry["message_id"] == str(payload.message_id) and
                role_entry["emoji"] == str(payload.emoji)):
            role = guild.get_role(int(role_entry["role_id"]))
            if role:
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
                print(f"Removed {role.name} from {member.name}")

# Endpoint para obtener la lista de roles desde un archivo JSON
@app.get("/roles")
def read_roles():
    return load_data()

# Registrar rutas adicionales
carpeta_api = os.path.join(os.path.dirname(__file__), 'Config')
router_principal = APIRouter()
registrar_rutas_desde_directorio(router_principal, carpeta_api)
app.include_router(router_principal)

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Función principal para ejecutar el bot y la API en paralelo
async def main():
    await asyncio.gather(
        asyncio.to_thread(run_api),
        bot.start(discord_token)
    )

asyncio.run(main())