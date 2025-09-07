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


print("Loading QUEEN (785d7b9f)")

os.makedirs("temp/", exist_ok=True)
with open("temp/audio.mp3", "wb") as f:
    f.write(
        requests.get("https://beta.sparebeat.com/api/tracks/785d7b9f/audio").content
    )
with open("temp/map.json", "wb") as f:
    f.write(requests.get("https://beta.sparebeat.com/api/tracks/785d7b9f/map").content)


load()
app.run()
