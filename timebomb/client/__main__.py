import cli
import curses
import time
import os
import requests

class MainMenu(cli.Window):

    dictionary = os.path.dirname(os.path.abspath(__file__)) + "/dict.txt"

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
        y = 50
        while y != 0:
            self.screen.clear()
            self.add_text(*self.centerize("Single player mode", {"x": 50, "y": y}))
            y -= 10
            time.sleep(1)
            self.refresh()

        self.add_text(*self.centerize("Press J to join!", {"x": 50, "y": 50}))
        self.add_text(*self.centerize("Press Q to return to main menu!", {"x": 50, "y": 90}))

        while True:
            key = self.screen.getch()
            if key in [ord("J"), ord("j")]:
                self.screen.clear()
                self.refresh()
                self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                self.add_text(*self.centerize("Loading Dictionary... (May use internet if you haven't downloaded this.)", {"x": 50, "y": 50}))
                if not os.path.exists(self.dictionary):
                    self.screen.clear()
                    self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                    self.add_text(*self.centerize("Loading Dictionary... (Downloading...)", {"x": 50, "y": 50}))
                    self.screen.refresh()
                    with open(self.dictionary, "w") as fp:
                        fp.write(requests.get("https://timebomb.api.timelessnesses.me/static/").content)
                self.screen.clear()
                self.refresh()
                self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                self.add_text(*self.centerize("Loading Dictionary... (Loading...)", {"x": 50, "y": 50}))
                with open(self.dictionary, "r") as fp:
                    self.dictionary_words = fp.read().splitlines()
                
            elif key in [ord("Q"), ord("q")]:
                self.screen.clear()
                self.refresh()
                return self.run()
            

if __name__ == "__main__":
    cli.run(MainMenu)
    print("Until we meet again!")
