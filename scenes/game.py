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

        # チャート読み込み
        self.chart = loadFromFile("temp/map.json")
        self.notes: List[Entity] = []
        self.events: List[Change] = sorted(
            self.chart.maps["hard"]["events"], key=lambda e: e.ms
        )
        # 判定
        self.perfects = 0
        self.rushes = 0
        self.cools = 0
        self.misses = 0
        # 最大スコアとスコア
        self.score = 0
        self.maxScore = 0
        for note in self.chart.maps["hard"]["notes"]:
            if isinstance(note, Division):
                continue
            elif isinstance(note, LongNote):
                self.maxScore += 1
            else:
                if note.attack:
                    self.maxScore += 2
                else:
                    self.maxScore += 1
        print(self.maxScore)

        # レーンと背景
        self.lane = Entity(model="cube", color=color.black, scale=(25, 400, 0))
        self.lane_half = self.lane.scale.x / 2

        self.background = Entity(
            model="cube", color=color.rgb32(158, 206, 206), scale=(28, 400, 0), z=0.1
        )
        self.judgementLine = Entity(
            model="cube",
            color=color.rgba32(232, 75, 156, 127),
            y=-10,
            z=-0.02,
            scale=(25, 0.3, 0),
        )

        # レーン区切り線
        self.lines = [
            Entity(
                model="cube",
                color=color.rgb32(103, 103, 103),
                x=(-self.lane_half) + ((self.lane_half * 2 / 4) * (i + 1)),
                y=-6,
                z=-0.01,
                scale=(0.1, 400, 0),
            )
            for i in range(3)
        ]

        # カメラ
        camera.rotate((-48, 0, 0))
        camera.set_position((0, -20, -20))
        camera.fov = 90

        # スカイボックス
        self.sky = Sky(
            parent=camera,
            model="sky_dome",
            texture="assets/images/polygon",
            scale=9900,
            shader=unlit_shader,
            unlit=True,
            color=color.rgb32(100, 100, 100),
        )

        # スコア
        self.scoreText = Text(text="0000000")
        self.scoreText.size = 0.06
        self.scoreText.font = "./assets/fonts/NovaMono-Regular.ttf"
        self.scoreText.origin = (0.5, 0.5)
        self.scoreText.position = (0.8, 0.45)

        # 音声
        self.audio = ExAudio("temp/audio.mp3", volume=0.5)
        self.audio.load()
        self.audio.play()

    # ------------------------------------------------------
    # ユーティリティ関数
    # ------------------------------------------------------
    def getCurrentSpeed(self, ms: float) -> float:
        """指定時刻 ms における現在の速度を返す"""
        speed = 1.0
        for ev in self.events:
            if isinstance(ev, Change) and ev.speed is not None and ms >= ev.ms:
                speed = ev.speed
        return speed

    def integratedSpeedTime(self, startMs: float, endMs: float) -> float:
        """startMs → endMs の間の進行距離（時間×速度）を返す"""
        if startMs == endMs:
            return 0.0
        reverse = endMs < startMs
        if reverse:
            startMs, endMs = endMs, startMs

        # start 時点の速度
        speed = self.getCurrentSpeed(startMs)
        total, prevMs = 0.0, startMs

        for ev in self.events:
            if not isinstance(ev, Change) or ev.speed is None:
                continue
            if ev.ms <= startMs:
                continue
            if ev.ms >= endMs:
                break
            total += (ev.ms - prevMs) * speed
            prevMs, speed = ev.ms, ev.speed

        total += (endMs - prevMs) * speed
        return -total if reverse else total

    def removeNote(self, note: Entity, reason: str):
        """ノーツ削除処理を統一"""
        if isinstance(note, LNEntity):
            note.unload()
        destroy(note)
        if note in self.notes:
            self.notes.remove(note)
        print(reason)
        if reason == "MISS":
            self.misses += 1

    def judgeNote(self, note: Entity, currentMs: float):
        """判定処理（通常 / LN 両対応）"""
        delta = currentMs - note.ms
        if abs(delta) < 35:
            print("PERFECT")
            self.score += 1
            self.perfects += 1
        elif delta > -100:
            print("RUSH")
            self.score += 0.5
            self.rushes += 1
        else:
            print("COOL")
            self.score += 0.5
            self.cools += 1

    # ------------------------------------------------------
    # ノーツ生成
    # ------------------------------------------------------
    def loadNote(self, note, nowSpeed: float):
        if isinstance(note, Note):
            color_ = (
                convertToColor(theme.themes[settings.theme].noteColors[note.key])
                if not note.attack
                else convertToColor(theme.themes[settings.theme].attackNoteColor)
            )
            scale_y = 2 if not note.attack else 1
            entity = Entity(
                model="diamond" if not note.attack else "cube",
                color=color_,
                x=constants.noteX[note.key],
                y=-10 - note.ms,
                z=-0.03,
                scale=((self.lane_half * 2 / 4), scale_y, 0),
            )
            entity.ms, entity.key = note.ms, note.key
            self.notes.append(entity)

        elif isinstance(note, LongNote):
            self.notes.append(LNEntity(note))

        elif isinstance(note, Division):
            entity = Entity(
                model="cube",
                color=color.rgb32(103, 103, 103),
                position=(0, -10 - note.ms, -0.03),
                scale=(25, 0.1, 0),
            )
            entity.ms, entity.key = note.ms, -1
            self.notes.append(entity)

        self.chart.maps["hard"]["notes"].remove(note)

    # ------------------------------------------------------
    # 更新処理
    # ------------------------------------------------------
    def update(self):
        if not self.audio.playing:
            return

        currentMs = self.audio.time
        nowSpeed = self.getCurrentSpeed(currentMs)
        movementPerMs = 0.03 * settings.playSpeed

        # ノーツ出現
        for note in self.chart.maps["hard"]["notes"].copy():
            if currentMs >= note.ms + 100:
                break
            if (
                note.ms - currentMs
                < 5000
                * window.aspect_ratio
                / settings.playSpeed
                / self.audio.pitch
                / abs(nowSpeed)
                and len([e for e in scene.entities if e.model and e.enabled]) - 5
                < max(70 * abs(nowSpeed), 50)
            ):
                self.loadNote(note, nowSpeed)

        # ノーツ移動 & 判定
        for note in self.notes.copy():
            integrated = self.integratedSpeedTime(note.ms, currentMs)
            note.y = -10 - (integrated * movementPerMs)

            if isinstance(note, LNEntity):
                # ロングノーツ
                totalLengthY = (
                    self.integratedSpeedTime(note.ms, note.ms + note.length)
                    * note.msToY
                )
                note.updateLength(totalLengthY)

                if currentMs < note.ms - 100:
                    continue

                if note.holding:
                    if held_keys[settings.reverseKeys[note.key]]:
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
                    elif abs(currentMs - (note.ms + note.length)) < 100:
                        self.removeNote(note, "MISS")
                elif currentMs - note.ms > 100:
                    note.missed = True
                    self.removeNote(note, "MISS")
                elif (
                    note.missed
                    and note.y < -20 * window.aspect_ratio
                    and currentMs - (note.ms + note.length) > 100
                ):
                    self.removeNote(note, "MISS")
            else:
                if note.y < -20 * window.aspect_ratio:
                    self.removeNote(note, "MISS")

        # オートプレイ
        if settings.autoPlay:
            for note in self.notes.copy():
                if note.key != -1 and currentMs - note.ms >= -30:
                    self.removeNote(note, "PERFECT")

        # スコア
        visibleScore = round(self.score / self.maxScore * 1e6)
        self.scoreText.text = (
            "1000000" if visibleScore == 1e6 else ("00000" + str(visibleScore))[-6:]
        )

        # 全ノーツ終了時のフェードアウト
        if (
            not self.notes
            and not self.chart.maps["hard"]["notes"]
            and self.audio.playing
        ):
            self.audio.fadeOut(0.25 * self.audio.pitch, 0)

    # ------------------------------------------------------
    # 入力処理
    # ------------------------------------------------------
    def input(self, key: str):
        try:
            if key.endswith("up"):
                keyName = key.split()[0]
                keyId = settings.keys.get(keyName, -1)
                if keyId < 0:
                    return

                currentMs = self.audio.time
                for note in self.notes.copy():
                    if (
                        isinstance(note, LNEntity)
                        and note.key == keyId
                        and note.holding
                    ):
                        delta = currentMs - (note.ms + note.length)
                        if abs(delta) <= 35:
                            print("PERFECT")
                            self.score += 1
                            self.perfects += 1
                        elif delta > -100:
                            print("RUSH")
                            self.score += 0.5
                            self.rushes += 1
                        else:
                            print("COOL")
                            self.score += 0.5
                            self.cools += 1
                        self.removeNote(note, "HIT")
                        return
            else:
                keyId = settings.keys.get(key, -1)
                if keyId < 0:
                    return

                currentMs = self.audio.time
                for note in self.notes.copy():
                    if note.key != keyId:
                        continue

                    if isinstance(note, LNEntity):
                        if not note.holding and abs(currentMs - note.ms) < 100:
                            note.holding = True
                        else:
                            return

                    if abs(currentMs - note.ms) < 100:
                        self.judgeNote(note, currentMs)
                        if not isinstance(note, LNEntity):
                            self.removeNote(note, "HIT")
                        return
        except KeyError:
            pass

    # ------------------------------------------------------
    # 後始末
    # ------------------------------------------------------
    def unload(self):
        for obj in [
            self.sky,
            self.background,
            self.lane,
            self.judgementLine,
            self.audio,
        ]:
            destroy(obj)
        for line in self.lines:
            destroy(line)
