import requests
import os

from ursina import Ursina

from scenes.game import GameScene

app = Ursina()

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
