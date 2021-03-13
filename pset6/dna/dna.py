from sys import argv
import csv


def main():

    # Python's sys module gives access to sys.argv for command line arguments.
    # Open a file "f" using open(filename), read conents with f.read().

    if len(argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")
        exit(1)

    # Open the CSV database file, read contents into memory.
    with open(argv[1]) as csvfile:
        database_csv = list(csv.reader(csvfile))  # Python's CSV module has reader and DictReader.

        # store the list of STRs in our database
        database_csv[0].remove("name")
        str_pattern = database_csv[0]  # Source: CSV library ref documentation

        # Open the TXT DNA sequence, read contents into memory.
        with open(argv[2]) as txtfile:
            sequence = txtfile.read()

        output_array = [0] * len(str_pattern)

        for i in range(len(str_pattern)):
            output_array[i] = str_analyser(sequence, str_pattern[i])  # Save STR counts in some data structure
            for row in database_csv[1:]:
                values = []
                for value in row[1:]:
                    values.append(int(value))  # Stored has string, convert to int
                    if values == output_array:  # turns out python lets us compare arrays :)
                        print(row[0])
                        exit(0)

    print("No match")
    exit(0)


def str_analyser(sequence, str_pattern):

    # For each STR, compute the longest run of consecutive repeats in the DNA sequence.

    counter = [0] * len(sequence)

    # For each position in the sequence: compute how many times the STR repeats starting at that position
    for i in range(len(sequence) - len(str_pattern)):  # for each STR, deternine its length, find in
        # Len(s) returns the length of string s, s[i:j] returns substrings from i to j (exclusive)
        if (sequence[i:(i+len(str_pattern))] == str_pattern):  # check if pattern exists and increase counter
            # for each position, keep checkiong succestive substrings until the STR repeats no longer
            counter[i] = counter[i-len(str_pattern)] + 1

    return max(counter)
    exit(0)


main()