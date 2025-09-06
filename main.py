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


print("Loading おぎゃりないざー (6183cb7e)")

os.makedirs("temp/", exist_ok=True)
with open("temp/audio.mp3", "wb") as f:
    f.write(
        requests.get("https://beta.sparebeat.com/api/tracks/6183cb7e/audio").content
    )
with open("temp/map.json", "wb") as f:
    f.write(requests.get("https://beta.sparebeat.com/api/tracks/6183cb7e/map").content)


load()
app.run()
