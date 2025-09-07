import ursina
from ursina import *
from ursina.shaders import unlit_shader

from sparebeat import loadFromFile, Note, Change, Division, LongNote
from models.longNote import LNEntity
from models.exAudio import ExAudio
from typing import List

from utils import constants, settings


class GameScene(Entity):
    def __init__(self):
        super().__init__()

        self.chart = loadFromFile("temp/map.json")
        self.notes: List[Entity] = []
        self.events: List[Change] = []

        self.lines: List[Entity] = []

        angle = -48

        camera.rotate((angle, 0, 0))
        camera.set_position((0, -20, -20))

        self.sky = Sky(
            parent=camera,
            name="sky",
            model="sky_dome",
            texture="assets/images/polygon",
            scale=9900,
            shader=unlit_shader,
            unlit=True,
            color=color.rgb32(100, 100, 100),
        )

        camera.fov = 90

        self.background = Entity(
            model="cube",
            color=color.rgb32(158, 206, 206),
            position=(0, 0, 0.1),
            rotation=(0, 0, 0),
            origin=(0, 0),
            scale=(28, 400, 0),
            collider="box",
        )

        self.lane = Entity(
            model="cube",
            color=color.black,
            position=(0, 0, 0),
            rotation=(0, 0, 0),
            origin=(0, 0),
            scale=(25, 400, 0),
            collider="box",
        )

        laneSize = self.lane.scale.x / 2

        for i in range(3):
            entity = Entity(
                model="cube",
                color=color.rgb32(103, 103, 103),
                position=((-laneSize) + ((laneSize * 2 / 4) * (i + 1)), -5.99, -0.01),
                rotation=(0, 0, 0),
                origin=(0, 0),
                scale=(0.1, 400, 0),
                collider="box",
            )
            self.lines.append(entity)

        self.judgementLine = Entity(
            model="cube",
            color=color.rgba32(232, 75, 156, 127),
            position=(0, -10, -0.02),
            rotation=(0, 0, 0),
            origin=(0, 0),
            scale=(25, 0.3, 0),
            collider="box",
        )

        """
        self.note = Entity(
            model="diamond",
            color=color.rgb32(102, 206, 207),
            rotation=(0, 0, 0),
            position=(
                0,
                6,
                -0.03,
            ),
            scale=((laneSize * 2 / 4), 2, 0),
        )

        self.text = Text(self.note.x)
        """

        self.events = sorted(self.chart.maps["hard"]["events"], key=lambda e: e.ms)

        self.clap = Audio("assets/sounds/clap", autoplay=False, loop=False, volume=2.0)

        self.audio = ExAudio("temp/audio.mp3", volume=0.5, pitch=1.0)
        self.audio.load()
        self.audio.play()

    def loadNote(self, note: Note):
        laneSize = self.lane.scale.x / 2

        if isinstance(note, Note):
            if not note.attack:
                entity = Entity(
                    model="diamond",
                    color=color.rgb32(102, 206, 207)
                    if note.key in [1, 2]
                    else color.rgb32(255, 255, 255),
                    rotation=(0, 0, 0),
                    position=(
                        constants.noteX[note.key],
                        -10 - note.ms,
                        -0.03,
                    ),
                    scale=((laneSize * 2 / 4), 2, 0),
                )
                entity.ms = note.ms
                entity.key = note.key
                self.notes.append(entity)
            else:
                entity = Entity(
                    model="cube",
                    color=color.rgb32(231, 74, 74),
                    rotation=(0, 0, 0),
                    position=(
                        constants.noteX[note.key],
                        -10 - note.ms,
                        -0.03,
                    ),
                    scale=((laneSize * 2 / 4), 1, 0),
                )
                entity.ms = note.ms
                entity.key = note.key
                self.notes.append(entity)
        elif isinstance(note, LongNote):
            entity = LNEntity(note, self.audio)
            self.notes.append(entity)
        elif isinstance(note, Division):
            entity = Entity(
                model="cube",
                color=color.rgb32(103, 103, 103),
                position=(0, -10 - note.ms, -0.03),
                rotation=(0, 0, 0),
                origin=(0, 0),
                scale=(25, 0.1, 0),
                collider="box",
            )
            entity.ms = note.ms
            entity.key = -1
            self.notes.append(entity)

        self.chart.maps["hard"]["notes"].remove(note)

    # Thanks for ChatGPT lol
    def integratedSpeedTime(self, startMs: float, endMs: float) -> float:
        """
        startMs -> endMs の間にノーツが「時間×速度」でどれだけ進むかを返す。
        endMs < startMs の場合は負の値を返す（将来のノーツに対しても対応）。
        """
        events = self.events  # すでにソートされている前提
        if startMs == endMs:
            return 0.0

        # 方向を正規化（常に start <= end にして、最後に符号を付ける）
        reverse = False
        if endMs < startMs:
            startMs, endMs = endMs, startMs
            reverse = True

        # start 時点の速度を見つける（startMs より前の最後のイベントの速度）
        speed = 1.0  # デフォルト速度（あなたの既存実装に合わせる）
        for ev in events:
            if not isinstance(ev, Change):
                continue
            if ev.speed is None:
                continue
            if ev.ms <= startMs:
                speed = ev.speed
            else:
                break

        total = 0.0
        prevMs = startMs

        for ev in events:
            if not isinstance(ev, Change):
                continue
            if ev.speed is None:
                continue
            if ev.ms <= startMs:
                continue
            if ev.ms >= endMs:
                break
            # prevMs 〜 ev.ms の区間は現在の speed で進む
            total += (ev.ms - prevMs) * speed
            prevMs = ev.ms
            speed = ev.speed

        # 最終区間
        total += (endMs - prevMs) * speed

        return -total if reverse else total

    def update(self):
        if self.audio.playing:
            currentMs = self.audio.time
            nowSpeed = 1.0
            for event in self.events:
                if isinstance(event, Change):
                    if event.speed is not None:
                        if currentMs >= event.ms:
                            nowSpeed = event.speed

            movementPerMs = 0.02 * settings.playSpeed
            # spawn notes
            for note in self.chart.maps["hard"]["notes"].copy():
                if currentMs >= note.ms + 100:
                    break
                if (
                    note.ms - currentMs
                    < 5000
                    * ursina.window.aspect_ratio
                    / settings.playSpeed
                    / self.audio.pitch
                    / abs(nowSpeed)
                    and max(
                        0, len([e for e in scene.entities if e.model and e.enabled]) - 5
                    )
                    < max(70 * abs(nowSpeed), 50)
                ):
                    self.loadNote(note)

            # move notes — ここを積分方式に変更
            for note in self.notes.copy():
                integrated = self.integratedSpeedTime(note.ms, currentMs)
                note.y = -10 - (integrated * movementPerMs)

                if note.y < -20 * ursina.window.aspect_ratio:
                    if isinstance(note, LNEntity):
                        note.unload()
                    destroy(note)
                    self.notes.remove(note)
                    if note.key != -1:
                        print("MISS")
                    continue

            if len(self.notes) <= 0 and len(self.chart.maps["hard"]["notes"]) <= 0:
                # self.audio.fade_out(0, 3, 3, curve.linear, destroy_on_ended=False)
                self.audio.fadeOut(3.0, 0)

    def input(self, key: str):
        keyId = -1
        if key == "d":
            keyId = 0
        if key == "f":
            keyId = 1
        if key == "j":
            keyId = 2
        if key == "k":
            keyId = 3

        if keyId >= 0:
            currentMs = self.audio.time
            for note in self.notes.copy():
                if note.key == keyId:
                    if abs(currentMs - note.ms) < 100:
                        if abs(currentMs - note.ms) < 35:
                            print("PERFECT")
                        elif currentMs - note.ms > -100:
                            print("RUSH")
                        else:
                            print("COOL")

                        if isinstance(note, LNEntity):
                            note.unload()
                        destroy(note)
                        self.notes.remove(note)
                        return

    def unload(self):
        destroy(self.sky)
        destroy(self.background)
        destroy(self.lane)
        destroy(self.judgementLine)
        for line in self.lines:
            destroy(line)
        destroy(self.audio)
