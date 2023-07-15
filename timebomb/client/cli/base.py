import curses
import art

class Window:
    """
    Main class for making anything useful on a fucking terminal
    """

    def __init__(self, screen: "curses._CursesWindow") -> None:
        screen.clear()
        curses.curs_set(0) 
        screen.nodelay(1) 
        screen.timeout(100)

curses.wrapper(Window)