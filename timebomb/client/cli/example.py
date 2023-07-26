import curses
import time

from base import Window


class Gay(Window):
    def run(window):
        # Calculate the progress bar length based on the terminal width
        def get_progress_bar_length():
            return int(width * 0.8)  # 80% of the terminal width

        # Game loop
        start_time = time.time()
        while True:
            window.screen.clear()

            # Get the updated terminal size
            height, width = window.screen.getmaxyx()

            # Calculate the coordinates for displaying the progress bar at the bottom
            progress_x, progress_y = window.get_coordinates(10, 90)

            # Calculate the coordinates for displaying the elapsed time in the middle
            time_x, time_y = window.get_coordinates(50, 50)

            # Calculate the progress bar length
            progress_bar_length = get_progress_bar_length()

            # Calculate the elapsed time
            elapsed_time = int(time.time() - start_time)

            # Display the progress bar
            progress = int((elapsed_time % 10) * (progress_bar_length / 10))
            window.add_text(
                {"x": progress_x, "y": progress_y},
                "[" + "#" * progress + "-" * (progress_bar_length - progress) + "]",
            )

            # Display the elapsed time
            time_text = "Elapsed Time: {}s".format(elapsed_time)
            time_x -= (
                len(time_text) // 2
            )  # Adjust the x-coordinate to center the text horizontally
            window.add_text({"x": time_x, "y": time_y}, time_text)

            # Refresh the screen
            window.refresh()

            # Get user input
            key = window.screen.getch()

            # Exit the game if 'q' is pressed
            if key == ord("q"):
                break


if __name__ == "__main__":
    curses.wrapper(Gay)
