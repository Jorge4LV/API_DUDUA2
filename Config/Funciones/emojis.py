import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

def get_emojis():
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/emojis"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emojis = response.json()
        emojis_data = [{"name": emoji["name"], "id": emoji["id"]} for emoji in emojis]
        
        with open("emojis_list.json", "w") as file:
            json.dump(emojis_data, file, indent=4)
        
        print("Emojis guardados en emojis_list.json")
    else:
        raise Exception(f"Failed to fetch emojis: {response.status_code}")

if __name__ == "__main__":
    get_emojis()