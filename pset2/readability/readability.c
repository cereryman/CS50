/* Readability test using Coleman-Liau index. */

#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <math.h>

/* Function prototypes */
int count_letters(string text);
int count_words(string text);
int count_sentences(string text);
float calc_index(int letters, int words, int sentences);
void tty_output(float index);

int main(void)
{
    string text        = get_string("Text: "); //Obtain text as input from user.

    int letters_nb     = count_letters(text); //Calculate the number of letters.
    int words_nb       = count_words(text); //Calculate the number of words.
    int sentences_nb   = count_sentences(text); //Calculate the number of sentences.
    float index        = calc_index(letters_nb, words_nb, sentences_nb); //Calculate the index.

    tty_output(index); //Output grade to tty.

}

int count_letters(string text)
{
    int n = 0, i = 0;
    while (text[n] != '\0')
    {
        /* Check if character is alphanumeric. */
        if (isalnum(text[n]) > 0)
        {
            i++;
        }
        n++;
    }
    return i;
}

int count_words(string text)
{
    int n = 0, i = 0;
    while (text[n] != '\0')
    {
        /* Check string for ASCII, whitespace characters or new line. */
        if (text[n] == ' ' || text[n] == '\n')
        {
            i++;
        }
        n++;
    }
    /* Increment word count for last word. */
    i++;
    return i;
}

int count_sentences(string text)
{
    int n = 0, i = 0;
    while (text[n] != '\0')
    {
        /* Check string for punctuation. */
        if (text[n] == '.' || text[n] == '!' || text[n] == '?')
        {
            i++;
        }
        n++;
    }
    return i;
}

float calc_index(int letters, int words, int sentences)
{
    /*Coleman-Liau index = 0.0588 * L - 0.296 * S - 15.8, where:
    - L is the average number of letters per 100 words
    - S is the average number of sentences per 100 words.*/

    const float c1 = 0.0588, c2 = -0.296, c3 = -15.8; //Initialize constants.

    float l = (100 * (float) letters) / (float) words; //Calculate "L" parameter (Note: typecast to avoid truncation).
    float s = (100 * (float) sentences) / (float) words; //Calculate "S" parameter (Note: typecast to avoid truncation).

    float index = c1 * l + c2 * s + c3; //Calculate Coleman-Liau index.

    return index;

}

void tty_output(float index)
{
    if (index >= 16)
    {
        printf("Grade 16+\n"); //Output default text for index >= 16 to tty.
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n"); //Output default text for index < 1 to tty.
    }
    else
    {
        printf("Grade %i\n", (int) roundf(index)); //Output grade to tty.
    }
}