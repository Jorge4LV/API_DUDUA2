from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import random

app = FastAPI()

# URL del archivo JSON en tu repositorio de GitHub
GITHUB_JSON_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repositorio/main/gifs.json"


class GifResponse(BaseModel):
    url: str
    name: str
    description: str


def fetch_gif_data():
    """
    Descarga y parsea el archivo JSON desde el repositorio de GitHub.
    """
    try:
        response = requests.get(GITHUB_JSON_URL)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching GIF data: {response.status_code}"
            )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/gif/", response_model=GifResponse)
def get_random_gif(category: str = None):
    """
    Devuelve un GIF aleatorio, filtrado opcionalmente por categoría.
    """
    data = fetch_gif_data()
    gifs = data.get("gifs", [])

    if category:
        gifs = [gif for gif in gifs if gif["category"] == category]
        if not gifs:
            raise HTTPException(status_code=404, detail="No GIFs found for this category.")

    selected_gif = random.choice(gifs)
    return GifResponse(
        url=selected_gif["url"],
        name=selected_gif["name"],
        description=selected_gif["description"]
    )


@app.get("/api/gifs/", response_model=list[GifResponse])
def list_all_gifs():
    """
    Devuelve una lista de todos los GIFs disponibles.
    """
    data = fetch_gif_data()
    gifs = data.get("gifs", [])
    return [
        GifResponse(
            url=gif["url"],
            name=gif["name"],
            description=gif["description"]
        )
        for gif in gifs
    ]