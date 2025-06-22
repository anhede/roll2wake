from components.screen import Screen
from components.potentiometer import Potentiometer
from components.pushbutton import PushButton
from components.utils import smart_wrap
import time

def scroll_read(
    screen: Screen,
    pot: Potentiometer,
    pushb: PushButton,
    text: str,
):
    """
    Shows the text on the screen, allows scrolling through it
    using the potentiometer.
    """
    if not text:
        return  # Nothing to scroll

    screen.set_cursor(True)
    # Split text into lines for display
    lines = text.split("\n")
    top_line = 0
    last_selected_line = -1
    while not pushb.is_pressed():
        selected_line = pot.read_discrete(len(lines))
        print(f"Selected line: {selected_line}, Top line: {top_line}")
        # Adjust top line such that selected line is visible
        if top_line + screen.rows <= selected_line:
            top_line = selected_line - screen.rows + 1
        elif top_line > selected_line:
            top_line = selected_line

        if last_selected_line != selected_line:
            last_selected_line = selected_line
            screen.message("\n".join(lines[top_line : top_line + screen.rows]))
            cursor_row = selected_line - top_line
            # Cursor row last character on the selected line
            cursor_col = min(len(lines[selected_line]), screen.cols - 1)
            screen.set_cursor_position(cursor_row, cursor_col)

        time.sleep(0.1)

    # Cleanup
    screen.set_cursor(False)
    screen.clear()


if __name__ == "__main__":
    # Example usage with mock components
    screen = Screen(20, 21)
    pot = Potentiometer(28)
    pushb = PushButton(15)

    # Sample text to scroll
    sample_text = smart_wrap(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque neque orci, tempor sit amet gravida sed, accumsan in lectus. Suspendisse potenti. Vestibulum ac tellus lobortis, elementum arcu vitae, aliquam nisl. Mauris et molestie neque, a bibendum lorem. Cras gravida orci non auctor finibus. Vivamus placerat, lacus sed suscipit cursus, dui odio efficitur neque, nec varius mauris elit nec enim. Aliquam erat volutpat. Integer vulputate eu massa a condimentum. Integer non justo eget ex placerat cursus hendrerit mattis magna.",
        row_len=screen.cols,
        max_rows=20,
    )

    scroll_read(screen, pot, pushb, sample_text)
