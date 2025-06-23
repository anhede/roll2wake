def smart_wrap(text: str, row_len: int, max_rows: int, center: bool = False) -> str:
    """
    Wraps the input text into lines no longer than row_len characters, up to max_rows lines.
    Splits on spaces when possible; if a word is longer than 12 characters, splits it into chunks of size row_len.
    Optionally centers each line by padding spaces on both sides until its length equals row_len.

    :param text: The input string to wrap.
    :param row_len: Maximum number of characters per line.
    :param max_rows: Maximum number of lines in the output.
    :param center: Whether to center each line by padding spaces.
    :return: Wrapped (and optionally centered) string with newline characters.
    """
    # Preprocess long words (>12 chars) into chunks of size row_len
    tokens = []
    for word in text.split():
        if len(word) > 12:
            for i in range(0, len(word), row_len):
                tokens.append(word[i : i + row_len])
        else:
            tokens.append(word)

    lines = []
    current = ""

    for token in tokens:
        # If token itself is longer than row_len, split it
        while len(token) > row_len:
            chunk, token = token[:row_len], token[row_len:]
            if current:
                lines.append(current)
                current = ""
                if len(lines) >= max_rows:
                    break
            lines.append(chunk)
            if len(lines) >= max_rows:
                break
        if len(lines) >= max_rows:
            break

        # Try to place token on current line
        if not current:
            current = token[:row_len]
        else:
            if len(current) + 1 + len(token) <= row_len:
                current += " " + token
            else:
                lines.append(current)
                if len(lines) >= max_rows:
                    break
                current = token
    else:
        # Append leftover content if not over max_rows
        if current and len(lines) < max_rows:
            lines.append(current)

    # Truncate to max_rows
    lines = lines[:max_rows]

    # Optionally center each line by padding spaces
    if center:
        centered_lines = []
        for line in lines:
            pad_total = row_len - len(line)
            left_pad = pad_total // 2
            right_pad = pad_total - left_pad
            centered_lines.append(" " * left_pad + line + " " * right_pad)
        lines = centered_lines

    return "\n".join(lines)


def time_string(
    include_date: bool = False,
    include_seconds: bool = True,
    prefix_day_of_week: bool = False,
) -> str:
    """
    Returns the current time as a formatted string, optionally including the date,
    seconds, and the day of the week.

    :param include_date: If True, includes the date (YYYY-MM-DD).
    :param include_seconds: If True, includes seconds in the output.
    :param prefix_day_of_week: If True, prefixes the output with the day name (e.g., 'Monday').
    Compatible with MicroPython.
    """
    import utime

    # Get current local time tuple
    t = utime.localtime()
    # MicroPython localtime tuple: (year, month, day, hour, minute, second, weekday, yearday)
    # weekday: 0 = Monday, 6 = Sunday
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = ""
    if prefix_day_of_week:
        # Safely get the weekday name
        dow = days[t[6]] if 0 <= t[6] < len(days) else ""

    # Build date and time parts
    if include_date:
        date_part = "{:04}-{:02}-{:02}".format(t[0], t[1], t[2])
        if include_seconds:
            time_part = "{:02}:{:02}:{:02}".format(t[3], t[4], t[5])
        else:
            time_part = "{:02}:{:02}".format(t[3], t[4])
        result = f"{date_part} {time_part}"
    else:
        if include_seconds:
            result = "{:02}:{:02}:{:02}".format(t[3], t[4], t[5])
        else:
            result = "{:02}:{:02}".format(t[3], t[4])

    # Prefix the day of the week if requested
    if prefix_day_of_week and dow:
        return f"{dow} {result}"
    return result


# Example usage
if __name__ == "__main__":
    sample = "This function will smartly split a long string into multiple lines based on the given row length and number of rows."
    print("Left-aligned:")
    print(smart_wrap(sample, row_len=30, max_rows=4, center=False))
    print("\nCentered:")
    print(smart_wrap(sample, row_len=30, max_rows=4, center=True))
    print("\nCurrent time:", time_string(include_date=True, include_seconds=True, prefix_day_of_week=True))
