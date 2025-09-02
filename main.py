from ursina import Ursina

from scenes.game import GameScene

app = Ursina()

currentScene = None


def load():
    global currentScene
    if currentScene:
        currentScene.unload()
    currentScene = GameScene()


load()

app.run()
