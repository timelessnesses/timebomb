import cli
import curses

class MainMenu(cli.Window):
    def run(self) -> None:
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        last_x, last_y = self.width, self.height

        while True:
            if self.width != last_x or last_y != self.height:
                self.screen.clear()
                last_x = self.width
                last_y = self.height
                self.refresh()
            self.add_text(*self.centerize("Time bomb!", {"x": 50, "y": 20}), curses.A_REVERSE)
            self.add_text(*self.centerize("Made by timelessnesses (https://timelessnesses.me)", {"x": 50, "y":40}))
            self.add_text(*self.centerize("Options", {"x": 50,"y": 60}))
            self.add_text(*self.centerize("(S)ingleplayer                             (M)ultiplayer                             (Q)uit", {"x": 50,"y": 80}))
            key = self.screen.getch()
            if key in [ord("S"), ord("s")]:
                self.single_player_initialize()
            elif key in [ord("M"), ord("m")]:
                self.multi_player_initialize()
            elif key in [ord("Q"), ord("q")]:
                break
            else:
                continue

    def single_player_initialize(self) -> None:
        self.screen.clear()
        self.add_text(self.centerize("Single player mode", {}))

if __name__ == "__main__":
    cli.run(MainMenu)
    print("Until we meet again!")
