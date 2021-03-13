// A program that implements a substitution cipher.

#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

/* Function prototypes */
int containsnonalpha(string argv);
int containsduplicate(string argv);
string encipher(string key, string plaintext);

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        /* Too many or too few input argument(s). */
        printf("Usage: ./substitution key\n");
        return 1;
    }
    else if (containsnonalpha(argv[1]) == 1)
    {
        /* Input argument contains not alphabetic characters */
        printf("Key must only contain alphabetic characters.\n");
        return 1;
    }
    else if (containsduplicate(argv[1]) == 1)
    {
        /* Input argument contains repeated character(s) */
        printf("Key must not contain repeated characters.\n");
        return 1;
    }
    else if (strlen(argv[1]) != 26)
    {
        /* Input argument doesn't contain 26 characters. */
        printf("Key must contain 26 characters.\n");
        return 1;
    }
    else
    {
        /* Input argument is okay, program starts here */
        string plaintext = get_string("plaintext: "); //Obtain text as input from user.
        string cryptedstring = encipher(argv[1], plaintext);
        printf("ciphertext: %s\n", cryptedstring);
        return 0;
    }
}

int containsnonalpha(string argv)
{
    int n = 0, i = 0;

    while (argv[n] != '\0')
    {
        /* Check string for non alphabetic characters. */
        if (isalpha(argv[n]) == 0)
        {
            return 1;
        }
        else
        {
            n++;;
        }
    }
    return 0;
}

int containsduplicate(string argv)
{
    int i = 0, j = 0;

    int  len = strlen(argv); // Find length of string.

    /* Check for duplicate */
    for (i = 0; i < len; i++)
    {
        for (j = i + 1; j < len; j++)
        {
            if (tolower(argv[i]) == tolower(argv[j]))
            {
                return 1;
            }
        }
    }

    return 0;

}

string encipher(string key, string plaintext)
{
    /* Store alphabet for each letter in array as follow. Use UPPERCASE.
    Index   Letter
    0      -> A
    1      -> B
    2      -> C
    3      -> D
    4      -> E
    5      -> F
    6      -> G
    7      -> H
    8      -> I
    9      -> J
    10     -> K
    11     -> L
    12     -> M
    13     -> N
    14     -> O
    15     -> P
    16     -> Q
    17     -> R
    18     -> S
    19     -> T
    20     -> U
    21     -> V
    22     -> W
    23     -> X
    24     -> Y
    25     -> Z */

    string alpha_block = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    string cryptedtext = plaintext; // To make sure correct space is reserved in memory.

    int textlen = strlen(cryptedtext); // To make sure we only check for the correct length.
    int alphalen = strlen(alpha_block); // Not needed, but making it dynamic, just in case the alphabet changes one day...
    int i = 0, j = 0;

    bool success; // Success flag, so loop stops executing once letter is found.

    for (i = 0; i < textlen; i++)
    {
        success = 0;
        for (j = 0; j < alphalen && success == 0; j++)
        {
            if (islower(plaintext[i]) > 0)
            {
                if (toupper(plaintext[i]) == alpha_block[j])
                {
                    cryptedtext[i] = tolower(key[j]);
                    success = 1;
                }
            }
            else
            {
                if ((plaintext[i]) == alpha_block[j])
                {
                    cryptedtext[i] = toupper(key[j]);
                    success = 1;
                }
            }
        }
    }
    return cryptedtext;
}