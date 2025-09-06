from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union


@dataclass
class BindZone:
    ms: int
    length: int


@dataclass
class Change:
    ms: int
    speed: Optional[float] = None
    bpm: Optional[int] = None
    barLine: Optional[bool] = None


@dataclass
class Note:
    ms: int
    key: int
    attack: bool


@dataclass
class LongNote:
    ms: int
    length: int
    key: int


@dataclass
class Division:
    ms: int


@dataclass
class LevelData:
    easy: int
    normal: int
    hard: int


@dataclass
class Info:
    title: str
    artist: str
    url: str
    bgColor: List[str]
    bpm: int
    startTime: int
    level: LevelData
    maps: Dict[
        Literal["easy", "normal", "hard"],
        Dict[Literal["notes", "events"], List[Union[Note, LongNote, Division, Change]]],
    ]
