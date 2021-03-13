import cs50
import csv
import sys


def main():

    # Initialize local variable(s)
    names = []

    # Check the command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python import.py characters.csv")
        exit(1)

    # Set the SQL database
    db = cs50.SQL("sqlite:///students.db")

    # Open the CSV characters file, read contents into memory.
    with open(sys.argv[1]) as csvfile:
        # Create DictReader
        characters_csv = csv.DictReader(csvfile)  # Python's CSV module has reader and DictReader.

    # Iterate over CSV file
        for row in characters_csv:

            # For each row, parse name
            # Use split methods on strings to split into words
            name = row["name"].split()

            # debug print(f"Currently Processing: {name}")

            # Second submission to change middle name to None, not 'None' if not existing
            house = row["house"]
            birth = row["birth"]

            if (len(name) == 3):  # Student has a middle name
                first = name[0]
                middle = name[1]
                last = name[2]
                # Insert each student into the "students table of "students.db"
                db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES(?, ?, ?, ?, ?)",
                           first, middle, last, house, birth)
            else:  # Student does not have a middle name
                first = name[0]
                last = name[1]
                # Second submission to change middle name to None, not 'None' if not existing (simply leave blank)
                db.execute("INSERT INTO students (first, last, house, birth) VALUES(?, ?, ?, ?)",
                           first, last, house, birth)

    exit(0)


main()