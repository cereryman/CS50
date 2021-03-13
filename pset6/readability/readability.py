from cs50 import get_string


def main():

    # Almost an exact copy of the "c" version. I understand that I could
    # "abstractize" this more due to the high level nature of Python.
    # However I am busy this week and have less time to dedicate to this than I would like.

    text = get_string("Text: ")

    letters_nb = count_letters(text)
    words_nb = count_words(text)
    sentences_nb = count_sentences(text)
    index = calc_index(letters_nb, words_nb, sentences_nb)

    # debug    print(f"{letters_nb}")
    # debug    print(f"{words_nb}")
    # debug    print(f"{sentences_nb}")

    if (index > 16):
        print(f"Grade 16+")  # Above 16, return "Grade 16+"
    elif (index < 1):
        print(f"Before Grade 1")  # Below 1, return "Before Grade 1"
    else:
        print(f"Grade {round(index)}")  # Need to properly round the value to the nearest integer (not truncate)


def count_letters(text):

    letters = 0

    for i in range(len(text)):
        if(text[i].isalnum()):  # To avoid counting spaces or other things.
            letters = letters + 1  # Increment by 1 each time.

    return letters  # Return the number of letters.


def count_words(text):

    words = 0

    for i in range(len(text)):
        if(text[i] == ' ' or text[i] == '\n'):  # Check for space or new line to determine a new word
            words = words + 1  # Increment by 1 each time.

    words = words + 1  # +1 is required for the last word.
    return words  # return the number of words.


def count_sentences(text):

    sentences = 0

    for i in range(len(text)):
        if(text[i] == '.' or text[i] == '!' or text[i] == '?'):  # Check for punctuation to determine a new sentence
            sentences = sentences + 1  # Increment by 1 each time.

    return sentences  # return the number of sentences.


def calc_index(letters, words, sentences):
    # Coleman-Liau index = 0.0588 * L - 0.296 * S - 15.8, where:
    # - L is the average number of letters per 100 words
    # - S is the average number of sentences per 100 words.

    c1 = 0.0588  # Constant 1 can be changed.
    c2 = -0.296  # Constant 2 can be changed.
    c3 = -15.8  # Constant 3 can be changed.

    # Compute average words/sentences per 100 words.
    l = (100 * letters) / words
    s = (100 * sentences) / words

    return c1 * l + c2 * s + c3  # Return the index


main()
