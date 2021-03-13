#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max voters and candidates
#define MAX_VOTERS 100
#define MAX_CANDIDATES 9

// preferences[i][j] is jth preference for voter i
int preferences[MAX_VOTERS][MAX_CANDIDATES];

// Candidates have name, vote count, eliminated status
typedef struct
{
    string name;
    int votes;
    bool eliminated;
}
candidate;

// Array of candidates
candidate candidates[MAX_CANDIDATES];

// Numbers of voters and candidates
int voter_count;
int candidate_count;

// Function prototypes
bool vote(int voter, int rank, string name);
void tabulate(void);
bool print_winner(void);
int find_min(void);
bool is_tie(int min);
void eliminate(int min);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: runoff [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX_CANDIDATES)
    {
        printf("Maximum number of candidates is %i\n", MAX_CANDIDATES);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i].name = argv[i + 1];
        candidates[i].votes = 0;
        candidates[i].eliminated = false;
    }

    voter_count = get_int("Number of voters: ");
    if (voter_count > MAX_VOTERS)
    {
        printf("Maximum number of voters is %i\n", MAX_VOTERS);
        return 3;
    }

    // Keep querying for votes
    for (int i = 0; i < voter_count; i++)
    {

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            // Record vote, unless it's invalid
            if (!vote(i, j, name))
            {
                printf("Invalid vote.\n");
                return 4;
            }
        }

        printf("\n");
    }

    // Keep holding runoffs until winner exists
    while (true)
    {
        // Calculate votes given remaining candidates
        tabulate();

        // Check if election has been won
        bool won = print_winner();
        if (won)
        {
            break;
        }

        // Eliminate last-place candidates
        int min = find_min();
        bool tie = is_tie(min);

        // If tie, everyone wins
        if (tie)
        {
            for (int i = 0; i < candidate_count; i++)
            {
                if (!candidates[i].eliminated)
                {
                    printf("%s\n", candidates[i].name);
                }
            }
            break;
        }

        // Eliminate anyone with minimum number of votes
        eliminate(min);

        // Reset vote counts back to zero
        for (int i = 0; i < candidate_count; i++)
        {
            candidates[i].votes = 0;
        }
    }
    return 0;
}

// Record preference if vote is valid
bool vote(int voter, int rank, string name)
{

    /* 1. Look for candidate called "name".
    (I wanted to use a recursive algorithm for this.
    However, since we cannot add functions, using a simple linear algorithm.) */

    for (int i = 0; i < candidate_count; i++)
    {
        if (!strcmp(candidates[i].name, name)) //Compare the name in the candidates.
        {
            /* 2. If candidate is found, update "preferences" so that they are
            the voter's "rank" preference, and return "true". */
            preferences[voter][rank] = i;
            return true;
        }
    }

    /* 3. If no candidate found don't update any preference and return "false". */
    return false;
}

// Tabulate votes for non-eliminated candidates
void tabulate(void)
{

    int success = false;

    // 1. Update vote counts for all non-eliminated candidates

    for (int i = 0; i < voter_count; i++) // Scan Voters
    {
        success = false;
        for (int j = 0; j < candidate_count && success == false; j++) // Scan ranks
        {
            if (candidates[preferences[i][j]].eliminated == false)
            {
                candidates[preferences[i][j]].votes = candidates[preferences[i][j]].votes + 1;
                success = true;
            }
        }
    }
    return;
}

// Print the winner of the election, if there is one
bool print_winner(void)
{
    /* 1. If any candidate has more than half of the vote,
    print out their name and return "true". */

    // half of voters = voter_count / 2

    // Scan the candidates for winner.
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes > (voter_count / 2)) // Compare the name in the candidates.
        {
            printf("%s\n", candidates[i].name); // Print winners.
            return true;
        }
    }

    // 2. If noboy has won the election yet, return "false".
    return false;
}

// Return the minimum number of votes any remaining candidate has
int find_min(void)
{
    // Return the minimum number of votes of anyone still in the election.

    int min = candidates[0].votes;
    int index = 0;

    for (int i = 0; i < candidate_count; i++) // Find the "first" biggest value,
    {
        if (candidates[i].eliminated == false)
        {
            if (candidates[i].votes < min)
            {
                min = candidates[i].votes;
                index++;
            }
        }
    }

    return min;
}

// Return true if the election is tied between all candidates, false otherwise
bool is_tie(int min)
{
    // 1. Accepts the minumum number of votes "min" as input
    // 2. Returns "true" if the election is tied between all remaining candidates,
    //    and returns "false" otherwise.

    int counter_rem = 0, counter_min = 0;

    for (int i = 0; i < candidate_count && !candidates[i].eliminated; i++) // Find the "first" biggest value,
    {
        counter_rem++; // Count candidates still in the race.
        if (candidates[i].votes == min)
        {
            counter_min++; // Count candidates still in the race with vote count = min.
        }
    }

    /* If # of candidates still in the race is equal to
    candidates (still in the race) with vote count = 0. */
    if (counter_min == counter_rem)
    {
        return true;
    }

    return false;
}

// Eliminate the candidate (or candidates) in last place
void eliminate(int min)
{
    // 1. Eliminate anyone still in the race who has the "min" number of votes.

    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[i].votes == min && !candidates[i].eliminated)
        {
            candidates[i].eliminated = true;
        }
    }

    return;
}
