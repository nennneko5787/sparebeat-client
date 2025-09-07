from typing import Dict, List
from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Theme:
    noteColors: List[str]
    longColor: List[str]
    attackNoteColor: str


class ThemeType(StrEnum):
    MIKU = "39"


themes: Dict[ThemeType, Theme] = {
    ThemeType.MIKU: Theme(
        noteColors=["#FFFFFF", "#66CECF", "#66CECF", "#FFFFFF"],
        longColor=["#9A9A9A", "#66CECF", "#66CECF", "#9A9A9A"],
        attackNoteColor="#E74A4A",
    )
}
