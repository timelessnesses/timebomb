import curses
import time
import random
import art
def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(100)  # Set a timeout for getch() in milliseconds

    # Enable color mode
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)

    # Get the terminal size
    height, width = stdscr.getmaxyx()

    # Initial position and velocity
    x = width // 2
    y = height // 2
    velocity_x = 1
    velocity_y = 1

    # Text to display
    texts = "h"

    # Initial color pair
    color_pair = 1

    # Game loop
    while True:
        text = (random.choice(texts))
        # Update the position
        x += velocity_x
        y += velocity_y

        # Reverse direction if the text hits the screen edges
        if x <= 0 or x >= width - len(text):
            velocity_x *= -1
            # Change the text color randomly
            color_pair = curses.color_pair(random.choice(range(1,4)))
        if y <= 0 or y >= height - 1:
            velocity_y *= -1
            # Change the text color randomly
            color_pair = curses.color_pair(random.choice(range(1,4)))

        # Display the text at the current position with the current color
        stdscr.addstr(y, x, text, color_pair)

        # Refresh the screen
        stdscr.refresh()

        # Sleep for a short duration to control the animation speed
        time.sleep(0.1)

        # Get user input
        key = stdscr.getch()

        # Exit the game if 'q' is pressed
        if key == ord('q'):
            break

if __name__ == '__main__':
    curses.wrapper(main)
