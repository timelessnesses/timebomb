import curses
import time

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(1000)  # Set a timeout for getch() in milliseconds
    curses.noecho()
    curses.cbreak()

    # Get the terminal size
    height, width = stdscr.getmaxyx()

    # Calculate the coordinates based on the percentage position
    def get_coordinates(percent_x, percent_y):
        x = int(width * percent_x / 100)
        y = int(height * percent_y / 100)
        return x, y

    # Calculate the progress bar length based on the terminal width
    def get_progress_bar_length():
        return int(width * 0.8)  # 80% of the terminal width

    # Game loop
    start_time = time.time()
    while True:
        stdscr.clear()

        # Get the updated terminal size
        height, width = stdscr.getmaxyx()

        # Calculate the coordinates for displaying the progress bar at the bottom
        progress_x, progress_y = get_coordinates(10, 90)

        # Calculate the coordinates for displaying the elapsed time in the middle
        time_x, time_y = get_coordinates(50, 50)

        # Calculate the progress bar length
        progress_bar_length = get_progress_bar_length()

        # Calculate the elapsed time
        elapsed_time = int(time.time() - start_time)

        # Display the progress bar
        progress = int((elapsed_time % 10) * (progress_bar_length / 10))
        stdscr.addstr(progress_y, progress_x, '[' + '#' * progress + '-' * (progress_bar_length - progress) + ']')

        # Display the elapsed time
        time_text = 'Elapsed Time: {}s'.format(elapsed_time)
        time_x -= len(time_text) // 2  # Adjust the x-coordinate to center the text horizontally
        stdscr.addstr(time_y, time_x, time_text)

        # Refresh the screen
        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        # Exit the game if 'q' is pressed
        if key == ord('q'):
            break

if __name__ == '__main__':
    curses.wrapper(main)

