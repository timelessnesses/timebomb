import curses
import art
from .errors import ExceededPlacementPercentError
from .typesx import Coordinate
import string

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
            raise ExceededPlacementPercentError(f"{'percent_x' if percent_x > 100 else 'percent_y'} exceed over 100.")
        x = int(self.width * percent_x / 100)
        y = int(self.height * percent_y / 100)
        return x, y
    
    def add_text(self, pos: Coordinate, string: str) -> None:
        assert self.is_renderable(string), "Unrenderable"
        self.screen.addstr(pos["y"],pos["x"],string)

    def refresh(self):
        self.screen.refresh()

    def run(self) -> None:
        raise NotImplementedError("You should implement this function first by either put it with attributes or subclass this class then write it.")

    def is_renderable(self, s: str) -> bool:
        for c in s:
            if c not in string.printable:
                return False
        return True