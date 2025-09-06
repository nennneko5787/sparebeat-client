from ursina import *
from sparebeat import LongNote

from utils import constants, settings


class LNEntity(Entity):
    def __init__(self, note: LongNote, audio: Audio, **kwargs):
        super().__init__(**kwargs)
        self.audio = audio
        self.ms = note.ms
        self.length = note.length
        self.key = note.key

        # ms→座標変換係数
        self.msToY = 0.02 * settings.playSpeed

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

        # ロング本体
        self.long = Entity(
            parent=self,
            model="cube",
            color=color.rgb32(102, 206, 207)
            if note.key in [1, 2]
            else color.rgb32(154, 154, 154),
            scale=(25 / 4, self.length * self.msToY, 0),
            position=(0, (self.length * self.msToY) / 2, 0),
        )

        # テール
        self.endNote = Entity(
            parent=self,
            model="diamond",
            color=color.white,
            scale=(25 / 4, 2, 0),
            position=(0, (self.length * self.msToY), 0),
        )

    def unload(self):
        destroy(self.note)
        destroy(self.long)
        destroy(self.endNote)
