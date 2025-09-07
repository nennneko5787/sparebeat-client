from ursina import *
from sparebeat import LongNote

from utils import constants, settings, theme


class LNEntity(Entity):
    def __init__(self, note: LongNote, audio: Audio, spawnSpeed: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.audio = audio
        self.ms = note.ms
        self.length = note.length
        self.key = note.key

        self.holding = False

        # ms→座標変換係数
        self.msToY = 0.03 * settings.playSpeed

        # 初期位置（y は GameScene.update が動かすのでダミー）
        self.position = (
            constants.noteX[note.key],
            -10 - note.ms,
            -0.03,
        )

        # ヘッド
        self.note = Entity(
            parent=self,
            model="diamond",
            color=color.white,
            scale=(25 / 4, 2, 0),
            position=(0, 0, 0),
        )

        # ロング本体 — 出現時の速度を反映
        self.long = Entity(
            parent=self,
            model="cube",
            color=theme.themes[settings.theme].longColor[note.key],
            scale=(25 / 4, self.length * self.msToY * spawnSpeed, 0),
            position=(0, (self.length * self.msToY * spawnSpeed) / 2, 0),
        )

        # テール
        self.endNote = Entity(
            parent=self,
            model="diamond",
            color=color.white,
            scale=(25 / 4, 2, 0),
            position=(0, (self.length * self.msToY * spawnSpeed), 0),
        )

    def updateLength(self, length: float):
        self.long.scale_y = length
        self.long.y = length / 2
        self.endNote.y = length

    def unload(self):
        destroy(self.note)
        destroy(self.long)
        destroy(self.endNote)
