from .base import Window
from .errors import ExceededPlacementPercentError
from .typesx import Coordinate


def run(window: Window) -> None:
    import curses

    curses.wrapper(window)
