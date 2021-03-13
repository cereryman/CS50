#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string name = get_string("What is your name?\n"); //Obtain name as input from user.
    printf("hello, %s\n", name);
}
