import os
import requests
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
        for emoji in emojis:
            print(f"<:{emoji['name']}:{emoji['id']}>")
    else:
        raise Exception(f"Failed to fetch emojis: {response.status_code}")

if __name__ == "__main__":
    get_emojis()