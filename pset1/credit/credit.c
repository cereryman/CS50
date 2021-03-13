#include <cs50.h>
#include <stdio.h>

int lun_calc(unsigned long cc_number);
int lun_val(int lun);
int lengthcounter(unsigned long cc_number);
int card_check(unsigned long cc_number);
int extractor(unsigned long number, int position);

int main(void)
{

    unsigned long cc_number = get_long("Number:"); // Obtain CC number as input from user.

    int card = card_check(cc_number); // AMEX = 1, MC = 2, VISA = 3
    int lun = lun_calc(cc_number); // Local copy of the LUN.
    int lun_vall = lun_val(lun); // Local copy of LUN validty (0 = valid)

    /* Print result to tty and return 0*/
    if (lun_vall == 0 && card == 1)
    {
        printf("AMEX\n");
    }
    else if (lun_vall == 0 && card == 2)
    {
        printf("MASTERCARD\n");
    }
    else if (lun_vall == 0 && card == 3)
    {
        printf("VISA\n");
    }
    else
    {
        printf("INVALID\n");
    }

    return 0;
}

int lun_calc(unsigned long cc_number)
{

    /* This function calculated the LUN value for a CC number */
    int digit, digit2;
    int lun = 0, lun_1 = 0, lun_2 = 0;
    int len = lengthcounter(cc_number), len2;

    for (int i = 0; i < len; i++) // Extract every number from the CC number.
    {
        if (i % 2 > 0) // For every second number (starting from the end) = opposite since starting from the end.
        {
            digit = extractor(cc_number, i) * 2; // Multiply by 2
            len2 = lengthcounter(digit);
            for (int j = 0; j < len2; j++) //Seperate double digits into 2 seperate digits and sum all digits them.
            {
                digit2 = extractor(digit, j);
                lun_1 = lun_1 + digit2;
            }
        }
        else // Sum the remaining digits.
        {
            digit = extractor(cc_number, i);
            lun_2 = lun_2 + digit;
        }
    }

    lun = lun_1 + lun_2; // Sum the sums and return the LUN value.
    return lun;
}

int lun_val(int lun)
{
    /* LUN is valid if it ends with the number 0, check if remainder is 0 when divide by 10 */
    if (lun % 10 == 0)
    {
        return 0; // Valid
    }
    else
    {
        return 1; // Invalid
    }
}

int lengthcounter(unsigned long cc_number)
{
    // Calculate the length of the CC number. */
    int i = 0;
    unsigned long cc_numberl = cc_number; // Local version of CC number.

    while (cc_numberl > 0)
    {
        cc_numberl = cc_numberl / 10;
        i++;
    }

    return i;
}

int card_check(unsigned long cc_number)
{
    /* Check which type of card was entered based on the following rules:
    AMEX: 15 digits, starts with 34 or 37.
    MC: 16 digits, starts with 51-55
    VISA: 13 or 16 digits, starts with 4. */
    const int AMEX_len = 15, MC_VISA_len = 16, VISA_len = 13;
    int len = lengthcounter(cc_number);

    int digit1 = 0, digit2 = 0;

    // Calculate the leading numbers. Numbers are substracted by 1 and 2 because extractor function uses C convention (start from 0)
    if (len == AMEX_len)
    {
        digit1 = extractor(cc_number, AMEX_len - 1);
        digit2 = extractor(cc_number, (AMEX_len - 2));
    }
    else if (len == MC_VISA_len)
    {
        digit1 = extractor(cc_number, MC_VISA_len - 1);
        digit2 = extractor(cc_number, (MC_VISA_len - 2));
    }
    else if (len == VISA_len)
    {
        digit1 = extractor(cc_number, MC_VISA_len - 1);
    }
    else
    {
        return 0;
    }

    // Return CC type based on length and leading digits.
    if (len == AMEX_len && digit1 == 3 && (digit2 == 4 || digit2 == 7))
    {
        return 1; //AMEX
    }
    else if (len == MC_VISA_len && digit1 == 5 && (digit2 == 1 || digit2 == 2 || digit2 == 3 || digit2 == 4 || digit2 == 5))
    {
        return 2; //MC
    }
    else if (len == MC_VISA_len && digit1 == 4)
    {
        return 3; //VISA
    }
    else if (len == VISA_len && digit1 == 4)
    {
        return 3; //VISA
    }
    else
    {
        return 0;
    }
}


int extractor(unsigned long number, int position)
{
    /* Extracts from right to left.
    To split the unsigned long into its individual digits, from right to left, use:
    long % 10
    long / 10 % 10
    long / 100 % 10
    long / 1000 % 10
    ... */
    int i = 0;
    int digit;

    while (number > 0 && i <= position)
    {
        digit = number % 10;
        number = number / 10;
        i++;
    }

    return digit;
}