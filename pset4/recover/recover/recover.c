#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Define constants
#define JPG_BYTE1   0xff
#define JPG_BYTE2   0xd8
#define JPG_BYTE3   0xff
#define JPG_BYTE4   0xe0

#define BLK_SIZE    512
#define ELMNTSIZE   1

#define TRUE        1
#define FALSE       0

#define FILENAME_S  8 // XXXX.jpg = 8 bytes

// Typedef for BYTES
typedef uint8_t BYTE;

// Function Prototypes
int found_jpg(BYTE buffer[]);

int main(int argc, char *argv[])
{

    // Ensure proper usage
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    //Open memory file:
    FILE *f = fopen(argv[1], "r");

    if (f == NULL)
    {
        printf("Forensic image cannot be opened for reading.\n");
        return 1;
    }

    // Read files
    // fread(data, size, number, inptr);
    //    data: pointer to where to store data you're reading
    //    size: size of each element to read
    //    number: number of elements to read
    //    inptr: FILE * to read from

    BYTE buffer[BLK_SIZE];
    int success = FALSE;
    int first_jpg = TRUE;
    int counter = 0;
    char filename[FILENAME_S];
    FILE *img;

    while (fread(buffer, BLK_SIZE, ELMNTSIZE, f)) //Repeat until end of card (NEED TO MODIFY)
    {

        if (found_jpg(buffer)) // If start of a new JPEG
        {
            if (first_jpg) // If first JPEG, Executed on first pass only
            {
                first_jpg = FALSE;
            }
            else
            {
                fclose(img); // If not first JPG, close the "previous" file
            }

            sprintf(filename, "%03i.jpg", counter); // Print integer with 3 digits to a parameter name for a new filename
            img = fopen(filename, "w"); // Open a new file and begin writing
            if (img == NULL)
            {
                printf("Could not open output file for write.\n");
                return 1;
            }
            fwrite(buffer, BLK_SIZE, ELMNTSIZE, img);
            counter++;
        }
        else  // Still searching for a new JPG, keep writing data to the file
        {
            if (!first_jpg) // Avoid reading invalid memory
            {
                fwrite(buffer, BLK_SIZE, ELMNTSIZE, img);
            }
        }
    }

    // Close file(s)
    fclose(img);
    fclose(f);

    return 0;

}

int found_jpg(BYTE buffer[])
{

    /*
    Look for beginning of JPEG:
        Each JPEG starts with a distinct header
            0xff 0xd8 0xff from first byte to third byte, left to right.
            The fourth byte, meanwhile, is either 0xe0, 0xe1, 0xe2, 0xe3,
            0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed,
            0xee, or 0xef. Put another way, the fourth byte’s first four bits are 1110.
        JPEGs are sotred back-to-back in memory card
    */

    if (buffer[0] == JPG_BYTE1 && buffer[1] == JPG_BYTE2 && buffer[2] == JPG_BYTE3 && (buffer[3]  & 0xf0) == JPG_BYTE4)
    {
        return TRUE;
    }

    return FALSE;
}
