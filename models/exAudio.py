import sounddevice as sd
from pydub import AudioSegment
import numpy as np
import time


class ExAudio:
    def __init__(
        self, name: str, volume: float = 1.0, pitch: float = 1.0, delay: float = 0.0
    ):
        self.volume = volume
        self.pitch = pitch
        self.name = name
        self.delay = delay

        self.song: AudioSegment = None
        self.samples: np.ndarray = None
        self.stream: sd.OutputStream = None
        self.startTime = None  # 実際の再生開始時間（秒）
        self.pos = 0  # 再生位置（サンプル単位）

        # フェード用
        self._fade_target = None
        self._fade_start = None
        self._fade_duration = None
        self._fade_start_volume = None

    def load(self):
        song = AudioSegment.from_mp3(self.name)
        silence = AudioSegment.silent(
            duration=3000 + (self.delay * 0.03), frame_rate=song.frame_rate
        )
        silence = silence.set_channels(song.channels).set_sample_width(
            song.sample_width
        )

        self.song = silence + song

        samples = np.array(self.song.get_array_of_samples(), dtype=np.float32)

        # ステレオ対応
        if self.song.channels == 2:
            samples = samples.reshape((-1, 2))

        # 正規化（pydub → int16 スケールなので /32768）
        self.samples = samples / 32768.0

    def _callback(self, outdata, frames, time_info, status):
        if self.startTime is None:
            # 初めて呼ばれたとき → 正確な再生開始時間を保存
            self.startTime = time_info.outputBufferDacTime

        # --- フェード計算 ---
        if self._fade_target is not None:
            elapsed = time.perf_counter() - self._fade_start
            t = min(elapsed / self._fade_duration, 1.0)
            # 線形補間 (start → target)
            self.volume = (
                self._fade_start_volume
                + (self._fade_target - self._fade_start_volume) * t
            )
            if t >= 1.0:
                # フェード完了
                self._fade_target = None
                self.stop()

        end = self.pos + frames
        chunk = self.samples[self.pos : end]

        # 🔊 音量を適用
        chunk = chunk * self.volume

        if len(chunk) < len(outdata):
            # 最後のフレーム（余りを埋める）
            outdata[: len(chunk)] = chunk
            outdata[len(chunk) :] = 0
            raise sd.CallbackStop()
        else:
            outdata[:] = chunk

        self.pos = end

    def play(self):
        self.pos = 0
        self.startTime = None
        self.stream = sd.OutputStream(
            samplerate=self.song.frame_rate * self.pitch,
            channels=self.song.channels,
            callback=self._callback,
        )
        self.stream.start()

    @property
    def playing(self):
        return self.stream is not None

    @property
    def time(self):
        """現在の再生時間をミリ秒で返す（実際のDAC基準）"""
        if self.startTime is None:
            return 0.0
        return (time.perf_counter() - self.startTime) * 1000 * self.pitch

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def fadeOut(self, duration: float, target: float = 0.0):
        """
        非ブロッキングでフェードアウトする
        duration: フェードにかける時間 (単位わかりません)
        target: 最終的な音量 (0.0 ~ 1.0)
        """
        self._fade_target = target
        self._fade_start = time.perf_counter()
        self._fade_duration = duration
        self._fade_start_volume = self.volume
