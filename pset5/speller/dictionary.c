// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 10000; // To be tuned (performance vs memory)

// Hash table
node *table[N];

// Number of words
unsigned int word_counter = 0;
// Dictionary loaded?
bool loaded = false;

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    int bucket = 0;
    char str[strlen(word)];

    /* Convert to lowercase. (I know the help video suggested
    to use strcasecmp, however we need to convert to lower case for the
    hash function anyway...) */
    strcpy(str, word);
    for (int i = 0; i < strlen(word); i++)
    {
        str[i] = tolower(str[i]);
    }

    bucket = hash(str); // Which bucket is the word in?
    // printf("check function - bucket is %i\n for string %s\n", bucket, str); // debug
    if (table[bucket] != NULL) // If NULL, Bucket doesn't exist, therefore word does not exist
    {
        // Search in the bucket for nodes containing string
        for (node *nodei = table[bucket]; nodei != NULL; nodei = nodei->next)
        {
            if (strcmp(str, nodei->word) == 0) // Compare strings
            {
                return true;
            }
        }
    }

    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // Takes a word as input
    // Outputs a number corresponding to which "bucket" to store the word in

    // Hash Function 1
    // Source: Doug's hashing function
    int sum = 0;
    for (int j = 0; word[j] != '\0'; j++)
    {
        sum += word[j];
    }

    return sum % N;

}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{

    FILE *fp; // Define file pointer
    char str[LENGTH + 1]; // String for file buffer
    int bucket;

    // Analysize buckets of size 0
    for (int i = 0; i < N; i++)
    {
        table[i] = NULL; // TODO -> modify
    }

    // Open dictionary file
    fp = fopen(dictionary, "r");  // Use fopen
    if (fp == NULL) // Check if return value is NULL
    {
        printf("fopen() - Error occured while open dictionary file%s.\n", dictionary);
        return false;
    }

    // Read strings from files one at a time
    while (fscanf(fp, "%s", str) != EOF) // fscanf will return EOF once it reaches the end of file
    {
        // Determine the bucket number
        bucket = hash(str);
        // printf("load function - bucket is %i\n for string %s\n", bucket, str); // debug

        // // Create a new node for each word
        node *n = malloc(sizeof(node)); // Use malloc to allocate
        if (n == NULL)
        {
            printf("malloc() - Error occured while allocating memory for word %s.\n", str);
            return false;
        }

        word_counter++;
        strcpy(n->word, str); // copy word into space in memory

        if (table[bucket] == NULL) // New bucket
        {
            n->next = NULL; // nothing comes after
            table[bucket] = n;
        }
        else // Add to existing bucket
        {
            node *tmp = table[bucket];
            while (tmp->next != NULL)
            {
                tmp = tmp->next;
            }
            tmp->next = n; // Link List element to word
        }

    }

    fclose(fp);
    loaded = true;
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    if (loaded)
    {
        return word_counter;
    }

    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{

    for (int bucket = 0; bucket < N; bucket++)
    {
        if (table[bucket] != NULL) // If NULL, Bucket doesn't exist, no memory allocated
        {
            // Search in the bucket for nodes containing data and free
            node *nodei = table[bucket];

            /* Based on check() function. But using while loop because
            we need to iterate node before clearing tmp */
            while (nodei != NULL)
            {
                node *tmp = nodei;
                nodei = nodei->next;
                free(tmp);
            }
        }
    }
    return true;
}
