from cs50 import get_int


def main():

    # Almost an exact copy of the "c" version. I understand that I could
    # "abstractize" this more due to the high level nature of Python.
    # However I am busy this week and have less time to dedicate to this than I would like.

    while True:
        height = get_int("Positive Integer: ")
        if(height > 0 and height <= 8):
            break

    pyramid(height)


def pyramid(height):
    hash = "#"  # Hash can be changed by anything.
    space = " "  # Space can be replaced by anything
    middle_spacing = 2  # "adjustable" middle spacing

    # See the first comment.

    for i in range(height):
        for j in range(height - (i + 1)):
            print(f"{space}", end="")
        for j in range(i + 1):
            print(f"{hash}", end="")
        for j in range(middle_spacing):
            print(f"{space}", end="")
        for j in range(i + 1):
            print(f"{hash}", end="")
        print("")


main()