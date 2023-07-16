import curses
import art
from .errors import ExceededPlacementPercentError
from .typesx import Coordinate
import string
from typing import Optional


class Window:
    """
    Main class for making anything useful on a fucking terminal
    """

    def __init__(self, screen: "curses._CursesWindow") -> None:
        screen.clear()
        curses.curs_set(0)
        screen.nodelay(1)
        screen.timeout(100)
        curses.start_color()
        curses.use_default_colors()
        self.screen = screen
        self.run()

    @property
    def width(self) -> int:
        return self.screen.getmaxyx()[1]

    @property
    def height(self) -> int:
        return self.screen.getmaxyx()[0]

    def get_coordinates(self, percent_x: float | int, percent_y: float | int):
        if percent_x > 100 or percent_y > 100:
            raise ExceededPlacementPercentError(
                f"{'percent_x' if percent_x > 100 else 'percent_y'} exceed over 100."
            )
        x = int(self.width * percent_x / 100)
        y = int(self.height * percent_y / 100)
        return x, y

    def add_text(self, pos: Coordinate, string: str, color_pair: Optional[int] = 0) -> None:
        assert self.is_renderable(string), "Unrenderable"
        x = self.get_coordinates(pos["x"], pos["y"])
        self.screen.addstr(x[1], x[0], string, color_pair)
        self.refresh()

    def refresh(self):
        self.screen.refresh()

    def run(self) -> None:
        raise NotImplementedError(
            "You should implement this function first by either put it with attributes or subclass this class then write it."
        )

    def is_renderable(self, s: str) -> bool:
        for c in s:
            if c not in string.printable:
                return False
        return True

    def arterize(self, string: str) -> str:
        return art.text2art(string)

    def centerize(self, string: str, pos: Coordinate) -> tuple:
        return ({"x": pos["x"] - len(string) // 2, "y": pos["y"]}, string)
