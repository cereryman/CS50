#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// Candidates have name and vote count
typedef struct
{
    string name;
    int votes;
}
candidate;

// Array of candidates
candidate candidates[MAX];

// Number of candidates
int candidate_count;

// Function prototypes
bool vote(string name);
void print_winner(void);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: plurality [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i].name = argv[i + 1];
        candidates[i].votes = 0;
    }

    int voter_count = get_int("Number of voters: ");

    // Loop over all voters
    for (int i = 0; i < voter_count; i++)
    {
        string name = get_string("Vote: ");

        // Check for invalid vote
        if (!vote(name))
        {
            printf("Invalid vote.\n");
        }
    }

    // Display winner of election
    print_winner();
}

// Update vote totals given a new vote
bool vote(string name)
{
    /* I wanted to use a recursive algorithm for this.
    However, since we cannot add functions, using a simple linear algorithm. */
    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(candidates[i].name, name) == 0) //Compare the name in the candidates.
        {
            candidates[i].votes++; //Add one vote to the candidate
            return true;
        }
    }

    return false;
}

// Print the winner (or winners) of the election
void print_winner(void)
{
    int max = candidates[0].votes; // Start at element 0, and comparing by moving through the array
    int index = 0;

    for (int i = 0; i < candidate_count; i++) // Find the "first" biggest value,
    {
        if (candidates[i].votes > max)
        {
            max = candidates[i].votes;
            index++;
        }
    }
    printf("%s\n", candidates[index].name); // Print the name for containing "first" biggest value

    /* Repeat the above process to find candidates
    with same # of votes as the one containing "first" biggest value */
    for (int j = 0; j < index; j++)
    {
        if (candidates[j].votes == candidates[index].votes)
        {
            printf("%s\n", candidates[j].name); // Print the names
        }
    }
    for (int k = (index + 1); k < candidate_count; k++)
    {
        if (candidates[k].votes == candidates[index].votes)
        {
            printf("%s\n", candidates[k].name); // Print the names
        }
    }

    return;
}