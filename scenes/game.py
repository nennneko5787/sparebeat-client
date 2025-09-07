import ursina
from ursina import *
from ursina.shaders import unlit_shader

from sparebeat import loadFromFile, Note, Change, Division, LongNote
from models.longNote import LNEntity
from models.exAudio import ExAudio
from typing import List

from utils import constants, settings, theme
from utils.color import convertToColor


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

        self.audio = ExAudio("temp/audio.mp3", volume=0.5, pitch=1.0)
        self.audio.load()
        self.audio.play()

    def loadNote(self, note: Note, nowSpeed: float):
        laneSize = self.lane.scale.x / 2

        if isinstance(note, Note):
            if not note.attack:
                entity = Entity(
                    model="diamond",
                    color=convertToColor(
                        theme.themes[settings.theme].noteColors[note.key]
                    ),
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
                    color=convertToColor(theme.themes[settings.theme].attackNoteColor),
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
        if not self.audio.playing:
            return

        currentMs = self.audio.time

        # 現在速度を取得
        nowSpeed = 1.0
        for event in self.events:
            if (
                isinstance(event, Change)
                and event.speed is not None
                and currentMs >= event.ms
            ):
                nowSpeed = event.speed

        movementPerMs = 0.03 * settings.playSpeed

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
                self.loadNote(note, nowSpeed)

        # move notes
        for note in self.notes.copy():
            if isinstance(note, LNEntity):
                # ノーツ長さ
                totalLengthY = (
                    self.integratedSpeedTime(note.ms, note.ms + note.length)
                    * note.msToY
                )

                if currentMs < note.ms - 100:
                    continue

                if note.holding:
                    if held_keys[settings.reverseKeys[note.key]]:
                        # 押し続けている場合
                        progressedY = (
                            self.integratedSpeedTime(
                                note.ms, min(currentMs, note.ms + note.length)
                            )
                            * note.msToY
                        )
                        remainingRatio = max(
                            0, (totalLengthY - progressedY) / totalLengthY
                        )
                        note.updateLength(totalLengthY * remainingRatio)
                        note.y = -10
                    else:
                        # 離した → ミス
                        note.unload()
                        destroy(note)
                        self.notes.remove(note)
                        print("MISS")
                        continue
                elif currentMs - note.ms > 100:
                    # ヘッドを押し損ね → ミス
                    note.unload()
                    destroy(note)
                    self.notes.remove(note)
                    print("MISS")
                    continue
            else:
                # 通常ノーツ
                integrated = self.integratedSpeedTime(note.ms, currentMs)
                note.y = -10 - (integrated * movementPerMs)

                # 画面外に出たら削除
                if note.y < -20 * ursina.window.aspect_ratio:
                    destroy(note)
                    self.notes.remove(note)
                    print("MISS")

        # オートプレイ
        if settings.autoPlay:
            for note in self.notes.copy():
                if note.key != -1 and currentMs - note.ms > -120:
                    if isinstance(note, LNEntity):
                        note.unload()
                    destroy(note)
                    self.notes.remove(note)
                    print("PERFECT")

        # 全ノーツ終了時のフェードアウト
        if (
            len(self.notes) <= 0
            and len(self.chart.maps["hard"]["notes"]) <= 0
            and self.audio.playing
        ):
            self.audio.fadeOut(0.25 * self.audio.pitch, 0)

    def input(self, key: str):
        try:
            if key.endswith("up"):
                keyName = key.split()[0]
                keyId = settings.keys.get(keyName, -1)
                if keyId < 0:
                    return
                currentMs = self.audio.time

                # LNEntity 終点判定
                for note in self.notes.copy():
                    if (
                        isinstance(note, LNEntity)
                        and note.key == keyId
                        and note.holding
                    ):
                        # ロングノーツ終点までの時間差
                        delta = currentMs - (note.ms + note.length)

                        if abs(delta) <= 35:
                            print("PERFECT")
                        elif delta > -100:
                            print("RUSH")
                        else:
                            print("COOL")

                        note.unload()
                        destroy(note)
                        self.notes.remove(note)
                        return
            else:
                # 通常ノーツ or LNヘッド判定
                keyId = settings.keys.get(key, -1)
                if keyId < 0:
                    return

                currentMs = self.audio.time
                for note in self.notes.copy():
                    if note.key != keyId:
                        continue

                    if isinstance(note, LNEntity):
                        # ヘッド判定
                        if not note.holding and abs(currentMs - note.ms) < 100:
                            note.holding = True
                            return
                    else:
                        # 通常ノーツ判定
                        if abs(currentMs - note.ms) < 100:
                            if abs(currentMs - note.ms) < 35:
                                print("PERFECT")
                            elif currentMs - note.ms > -100:
                                print("RUSH")
                            else:
                                print("COOL")

                            destroy(note)
                            self.notes.remove(note)
                            return
        except KeyError:
            pass

    def unload(self):
        destroy(self.sky)
        destroy(self.background)
        destroy(self.lane)
        destroy(self.judgementLine)
        for line in self.lines:
            destroy(line)
        destroy(self.audio)
