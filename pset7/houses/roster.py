import cs50
import sys


def main():

    # Check the command-line arguments
    if (len(sys.argv) != 2):
        print("Usage: python roster.py house")
        exit(1)

    # Set the SQL database
    db = cs50.SQL("sqlite:///students.db")

    # Query database for all students in house
    # output students (sorted by last name -> sort by first name) in this format:  name, born year
    # Use db.execute to SELECT rows from the table
    # Return the value is a list of python dicts,where each dict represents a row in the table
    db_output = db.execute("SELECT first, middle, last, birth FROM students WHERE house=%s ORDER BY last, first", sys.argv[1])
    # -> Source for "%s" format: https://pynative.com/python-mysql-execute-parameterized-query-using-prepared-statement/

    # Print out each student's full name and birth year
    for row in db_output:
        first = row["first"]
        middle = row["middle"]
        last = row["last"]
        birth = row["birth"]
        # Second revision to match changes to import function.
        # Turns out in Python, strings can be "falsey" :)
        if not middle:  # Check for NULL values for middle names
            print(f"{first} {last}, born {birth}")
        else:
            print(f"{first} {middle} {last}, born {birth}")

    exit(0)


main()