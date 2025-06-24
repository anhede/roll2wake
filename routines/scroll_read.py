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

    # Split text into lines for paging
    lines = text.split("\n")
    n = len(lines)
    h = screen.rows        # e.g. 4 on a 4×20 display
    step = h - 1           # overlap one line

    # Compute how many pages we need
    if n <= h:
        page_count = 1
    else:
        # ceil((n - h) / step) + 1
        page_count = ((n - h) + step - 1) // step + 1

    last_page = -1
    while not pushb.is_pressed():
        # get a page index between 0 and page_count-1
        page = pot.read_discrete(page_count)

        if page != last_page:
            last_page = page

            # compute top line for this page, clamped so we never run off the end
            top_line = page * step
            if top_line + h > n:
                top_line = n - h

            # grab exactly h lines and display them
            screen.message("\n".join(lines[top_line : top_line + h]))

        time.sleep_ms(50)


    # Cleanup
    screen.set_cursor(False)
    screen.clear()


if __name__ == "__main__":
    from components.pins import PIN_SCREEN_SDA, PIN_SCREEN_SCL, PIN_POT, PIN_BUTTON

    screen = Screen(PIN_SCREEN_SDA, PIN_SCREEN_SCL)
    pot = Potentiometer(PIN_POT)
    pushb = PushButton(PIN_BUTTON)

    # Sample text to scroll
    sample_text = smart_wrap(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque neque orci, tempor sit amet gravida sed, accumsan in lectus. Suspendisse potenti. Vestibulum ac tellus lobortis, elementum arcu vitae, aliquam nisl. Mauris et molestie neque, a bibendum lorem. Cras gravida orci non auctor finibus. Vivamus placerat, lacus sed suscipit cursus, dui odio efficitur neque, nec varius mauris elit nec enim. Aliquam erat volutpat. Integer vulputate eu massa a condimentum. Integer non justo eget ex placerat cursus hendrerit mattis magna.",
        row_len=screen.cols,
        max_rows=50,
    )

    scroll_read(screen, pot, pushb, sample_text)
