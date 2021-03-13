#include <cs50.h>
#include <stdio.h>

string pyramid(int height);

int main(void)
{
    int height;

    do
    {
        height = get_int("Height: ");
    }
    while (height < 1 || height > 8);

    pyramid(height);

}

string pyramid(int height)
{

    const string hash = "#";
    const string space = " ";
    const int middle_spacing = 2;

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < (height - (i + 1)); j++)
        {
            printf("%s", space); // Print L-H spaces
        }
        for (int j = 0; j < (i + 1); j++)
        {
            printf("%s", hash); // Print L-H hashes
        }
        for (int j = 0; j < middle_spacing; j++)
        {
            printf("%s", space); // Print middle spaces
        }
        for (int j = 0; j < (i + 1); j++)
        {
            printf("%s", hash); // Print R-H hashes
        }
        printf("\n");
    }
    return 0;
}