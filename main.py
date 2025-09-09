import requests
import os

from pathlib import Path
from ursina import *

from scenes.game import GameScene

application.asset_folder = Path("assets/")
application._model_path.append_path(str(application.fonts_folder.resolve()))

app = Ursina(title="sparebeat-player")

currentScene = None


def load():
    global currentScene
    if currentScene:
        currentScene.unload()
    currentScene = GameScene()


print("Loading ずんだパーリナイ (24e25a9c)")

os.makedirs("temp/", exist_ok=True)
with open("temp/audio.mp3", "wb") as f:
    f.write(
        requests.get("https://beta.sparebeat.com/api/tracks/24e25a9c/audio").content
    )
with open("temp/map.json", "wb") as f:
    f.write(requests.get("https://beta.sparebeat.com/api/tracks/24e25a9c/map").content)


load()
app.run()
