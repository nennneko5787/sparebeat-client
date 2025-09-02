import json
from typing import Dict, List, Union

from .objects import BindZone, Change, Division, Info, LevelData, LongNote, Note


def loadFromFile(path: str):
    with open(path, encoding="utf-8") as f:
        return loadFromDict(json.load(f))


def loadFromString(content: str):
    return loadFromDict(json.loads(content))


def loadFromDict(object: Dict[str, str]):
    title: str = object["title"]
    artist: str = object["artist"]
    url: str = object["url"]
    bgColor: List[str] = object["bgColor"]
    beats: int = object["beats"]
    bpm: int = object["bpm"]
    startTime: int = object["startTime"]
    level: Dict[str, int] = object["level"]
    _maps: Dict[str, List[Union[Dict[str, int], str]]] = object["map"]
    maps: Dict[str, List[Union[Note, LongNote, Change, Division]]] = {}

    for difficulty, map in _maps.items():
        _map = []
        _long = {}
        _bind = None
        _is2x = False
        _bpm = bpm
        globalMs = 0

        for data in map:
            if isinstance(data, dict):
                _map.append(
                    Change(
                        ms=globalMs,
                        speed=data.get("speed"),
                        bpm=data.get("bpm"),
                        barLine=data.get("barLine"),
                    )
                )
                if data.get("bpm"):
                    _bpm = data["bpm"]

            elif isinstance(data, str):
                for char in data:
                    _ichar = int(char) if char.isdigit() else -1
                    _ochar = ord(char)
                    _beat = 60000 / _bpm / ((beats / 2) if _is2x is True else beats)

                    if _ichar >= 1 and _ichar <= 4:
                        _map.append(Note(ms=globalMs, key=_ichar, attack=False))

                    elif _ichar >= 5 and _ichar <= 8:
                        _map.append(Note(ms=globalMs, key=_ichar - 4, attack=True))

                    elif _ochar >= 97 and _ochar <= 100:
                        _long[_ochar - 96] = globalMs

                    elif _ochar >= 101 and _ochar <= 104:
                        _map.append(
                            LongNote(
                                ms=_long[_ochar - 100],
                                length=(globalMs - _long[_ochar - 100]),
                                key=_ochar - 100,
                            )
                        )
                        del _long[_ochar - 100]

                    elif char == "(":
                        _is2x = True

                    elif char == ")":
                        _is2x = False

                    elif char == "[":
                        _bind = globalMs

                    elif char == "]":
                        _map.append(BindZone(ms=_bind, length=(globalMs - _bind)))
                        _bind = None

                    elif char == ",":
                        globalMs += _beat

                globalMs += _beat
                _map.append(Division(ms=globalMs))

        maps[difficulty] = _map

    return Info(
        title=title,
        artist=artist,
        url=url,
        bgColor=bgColor,
        beats=beats,
        bpm=bpm,
        startTime=startTime,
        level=LevelData(
            easy=level["easy"],
            normal=level["normal"],
            hard=level["hard"],
        ),
        maps=maps,
    )
