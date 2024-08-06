import discord
from discord.ext import commands
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
import json
import asyncio
import uvicorn
import os
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