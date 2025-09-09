import json
from typing import Dict, List, Union

from .objects import (
    BindZone,
    Change,
    Division,
    Info,
    LevelData,
    LongNote,
    Note,
)


def loadFromFile(path: str):
    with open(path, encoding="utf-8") as f:
        return loadFromDict(json.load(f))


def loadFromString(content: str):
    return loadFromDict(json.loads(content))


def loadFromDict(object: Dict[str, str]):
    title: str = object["title"]
    artist: str = object["artist"]
    url: str = object.get("url", "")
    bgColor: List[str] = object.get("bgColor", ["#43C6ACCC", "#191654CC"])
    bpm: int = object["bpm"]
    startTime: int = object["startTime"]
    level: Dict[str, int] = object["level"]
    _maps: Dict[str, List[Union[Dict[str, int], str]]] = object["map"]
    maps: Dict[str, List[Union[Note, LongNote, Change, Division]]] = {}

    for difficulty, map in _maps.items():
        _map = dict()
        _map["notes"] = []
        _map["events"] = []
        _long = [None, None, None, None]
        _bind = None
        _barLine = True
        _triplet = False
        _bpm = float(bpm) if isinstance(bpm, str) else bpm
        globalMs = 3000 + startTime

        for data in map:
            p = (1e3 / (_bpm / 60)) * 4

            def beat():
                if _triplet:
                    return p / 24
                else:
                    return p / 16

            if isinstance(data, dict):
                _map["events"].append(
                    Change(
                        ms=globalMs,
                        speed=data.get("speed"),
                        bpm=data.get("bpm"),
                        barLine=data.get("barLine"),
                    )
                )
                if data.get("bpm"):
                    _bpm = float(data["bpm"]) if isinstance(bpm, str) else data["bpm"]
                _barLine = data.get("barLine", _barLine)

            elif isinstance(data, str):
                for char in data:
                    _ichar = int(char) if char.isdigit() else -1
                    _ochar = ord(char)

                    if _ichar >= 1 and _ichar <= 4:
                        _map["notes"].append(
                            Note(ms=globalMs, key=_ichar - 1, attack=False)
                        )

                    elif _ichar >= 5 and _ichar <= 8:
                        _map["notes"].append(
                            Note(ms=globalMs, key=_ichar - 4 - 1, attack=True)
                        )

                    elif _ochar >= 97 and _ochar <= 100:
                        _long[_ochar - 97] = globalMs

                    elif _ochar >= 101 and _ochar <= 104:
                        _map["notes"].append(
                            LongNote(
                                ms=_long[_ochar - 101],
                                length=(globalMs - _long[_ochar - 101]),
                                key=_ochar - 101,
                            )
                        )
                        _long[_ochar - 101] = None

                    elif char == "(":
                        _triplet = True

                    elif char == ")":
                        _triplet = False

                    elif char == "[":
                        _bind = globalMs

                    elif char == "]":
                        try:
                            _map["events"].append(
                                BindZone(ms=_bind, length=(globalMs - _bind))
                            )
                            _bind = None
                        except Exception:
                            pass

                    elif char == ",":
                        globalMs += beat()

                globalMs += beat()
                if _barLine:
                    _map["notes"].append(Division(ms=globalMs))

        maps[difficulty] = _map

    return Info(
        title=title,
        artist=artist,
        url=url,
        bgColor=bgColor,
        bpm=bpm,
        startTime=startTime,
        level=LevelData(
            easy=level["easy"],
            normal=level["normal"],
            hard=level["hard"],
        ),
        maps=maps,
    )
