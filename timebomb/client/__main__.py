import cli
import curses
import time
import os
import requests
import random
import datetime

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
                        try:
                            fp.write(requests.get("https://timebomb.api.timelessnesses.me/dictionary").content.decode("utf-8"))
                        except Exception as e:
                            self.screen.clear()
                            self.refresh()
                            self.add_text(*self.centerize("Failed to download dictionary!", {"x": 50, "y": 50}))
                            time.sleep(2)
                            raise Exception("Cannot download and write it down to disk!") from e
                self.screen.clear()
                self.refresh()
                self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                self.add_text(*self.centerize("Loading Dictionary... (Loading...)", {"x": 50, "y": 50}))
                with open(self.dictionary, "r") as fp:
                    self.dictionary_words = fp.read().splitlines()
                    try:
                        assert len(self.dictionary_words) != 0, "Failed to extract dictionary"
                    except AssertionError as e:
                        self.screen.clear()
                        self.add_text(*self.centerize("Reloading single player...", {"x":50,"y": 50}))
                        os.remove(self.dictionary)
                        time.sleep(2)
                        self.single_player_initialize()
                        break
                self.screen.clear()
                self.refresh()
                
                health = 2
                streak = 0
                while health != 0:
                    self.screen.clear()
                    self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                    self.add_text(*self.centerize("Type the word containing these alphabets!", {"x": 50, "y": 30}))
                    if streak >= 5:
                        self.add_text(*self.centerize(self.generate_prompt(random.randint(1,3)), {"x": 50, "y": 80}))
                    elif streak >= 10:
                        self.add_text(*self.centerize(self.generate_prompt(random.randint(2,4)), {"x": 50, "y": 80}))
                    elif streak >= 15:
                        self.add_text(*self.centerize(self.generate_prompt(random.randint(3,5)), {"x": 50, "y": 80}))
                    else:
                        self.add_text(*self.centerize(self.generate_prompt(random.randint(1,2)), {"x": 50, "y": 80}))
                    self.add_text(*self.centerize(f"Answer: ", {"x": 50, "y": 90}))        
                    self.refresh()
                    now = datetime.datetime.now()
                    answer = ""
                    used = []
                    while True:
                        if (datetime.datetime.now() - now).total_seconds() >= 10:
                            health -= 1
                            streak = 0
                            break
                        key = self.screen.getch()
                        if key == curses.KEY_ENTER or key == 10:
                            # validate answer
                            if self.prompt in answer and answer not in used:
                                self.add_text(*self.centerize("Congratulations!",{"x":50, "y": 70}))
                                time.sleep(0.5)
                                self.screen.clear()
                                used.append(answer)
                                break
                            else:
                                answer = ""
                                self.add_text(*self.centerize("That didn't work.",{"x":50, "y": 70}))
                                time.sleep(0.5)
                                self.screen.clear()
                                self.add_text(*self.centerize("Type the word containing these alphabets!", {"x": 50, "y": 30}))
                                self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                                self.add_text(*self.centerize(self.prompt, {"x": 50, "y": 80}))
                                self.add_text(*self.centerize(f"Answer: {answer}", {"x": 50, "y": 90}))
                                continue
                        if key == curses.KEY_BACKSPACE or key == 8:
                            answer = answer[:-1]
                            self.screen.clear()
                            self.add_text(*self.centerize("Single player mode", {"x": 50, "y": 0}))
                            self.add_text(*self.centerize("Type the word containing these alphabets!", {"x": 50, "y": 30}))
                            self.add_text(*self.centerize(self.prompt, {"x": 50, "y": 80}))
                            self.add_text(*self.centerize(f"Answer: {answer}", {"x": 50, "y": 90}))
                            self.refresh()
                            continue
                        try:
                            if not self.is_renderable(chr(key)):
                                continue
                            answer += chr(key)
                            self.add_text(*self.centerize(f"Answer: {answer}", {"x": 50, "y": 90}))
                        except ValueError:
                            pass


                
                
            elif key in [ord("Q"), ord("q")]:
                self.screen.clear()
                self.refresh()
                return self.run()
            
    def generate_prompt(self, len: int) -> str:
        word = random.choice(self.dictionary_words)
        if random.randint(0,1) == 0:
            self.prompt = word[-len:]
            return self.prompt
        else:
            self.prompt = word[:len]
            return self.prompt

if __name__ == "__main__":
    cli.run(MainMenu)
    print("Until we meet again!")
