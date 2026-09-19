import re


def detect_section(text: str):
    """
    Detect the first numbered section heading.
    """

    lines = text.splitlines()

    for i, line in enumerate(lines):

        line = line.strip()

        # Match:
        # 1. Organisation...
        # 2. Finanzielles...
        # 2.1 Wachstum...
        match = re.match(
            r"^(\d+(?:\.\d+)?)\.\s+(.+)$",
            line
        )

        if match:

            section_number = match.group(1)
            section_title = match.group(2).strip()

            # If the heading continues onto the next line,
            # add that line to the title.
            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                # Only add it if it does NOT start
                # another numbered section.
                if next_line and not re.match(
                    r"^\d+(?:\.\d+)?\.\s+",
                    next_line
                ):
                    section_title += " " + next_line

            return f"{section_number}. {section_title}"

    return None


if __name__ == "__main__":

    test_text = """
    1. Organisation des Siemens-Konzerns und Grundlagen der
    Berichterstattung

    Siemens ist ein in nahezu allen Ländern der Welt aktiver
    Technologiekonzern.

    2. Finanzielles Steuerungssystem

    2.1 Wachstum der Umsatzerlöse
    """

    section = detect_section(test_text)

    print("Detected section:")
    print(section)