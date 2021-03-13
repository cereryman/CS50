#include "helpers.h"

#include <math.h> // Added the math library for the round() function

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{

    int average;
    /* to ensure each pixel of the new image still has the same general brightness
    or darkness as the old image, we can take the average of the red, green, and blue
    values to determine what shade of grey to make the new pixel. */
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            average = round((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0);
            image[i][j].rgbtBlue = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtRed = average;
        }
    }

    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    /* SepiaRed = .393 * originalRed + .769 * originalGreen + .189 * originalBlue
    sepiaGreen = .349 * originalRed + .686 * originalGreen + .168 * originalBlue
    sepiaBlue = .272 * originalRed + .534 * originalGreen + .131 * originalBlue */

    int sepia[3]; // 0 =  Blue, 1 = Green, 2 = Red.


    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {

            sepia[2] = round(.393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue);
            sepia[1] = round(.349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue);
            sepia[0] = round(.272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue);

            for (int  k = 0; k <= 2; k++)
            {
                if (sepia[k] > 255)
                {
                    sepia[k] = 255;
                }
            }

            image[i][j].rgbtBlue = sepia[0];
            image[i][j].rgbtGreen = sepia[1];
            image[i][j].rgbtRed = sepia[2];
        }
    }

    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    int temp[3];

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2 ; j++)
        {

            temp[0] = image[i][width - 1 - j].rgbtBlue;
            temp[1] = image[i][width - 1 - j].rgbtGreen;
            temp[2] = image[i][width - 1 - j].rgbtRed;

            image[i][width - 1 - j].rgbtBlue = image[i][j].rgbtBlue;
            image[i][width - 1 - j].rgbtGreen = image[i][j].rgbtGreen;
            image[i][width - 1 - j].rgbtRed = image[i][j].rgbtRed;

            image[i][j].rgbtBlue = temp[0];
            image[i][j].rgbtGreen = temp[1];
            image[i][j].rgbtRed =  temp[2];


        }
    }

    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{

    RGBTRIPLE image_copy[height][width];
    int new_refi, new_refj;
    int sum[3] = {0, 0, 0}; // Index = 0 Green, Index = 1 Blue, Index = 2 Red
    int divider = 0;

    // Create a new image so that blurring algorithm uses the original surrounding pixels and not the blurred ones.
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image_copy[i][j] = image[i][j];
        }
    }

    // blur the pixels; loop through the entire image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Loop through pixels -1 to +1 beside and on top/below of pixel.
            for (int delta_i = -1; delta_i <= 1; delta_i++)
            {
                for (int delta_j = -1; delta_j <= 1; delta_j++)
                {
                    new_refi = i + delta_i;
                    new_refj = j + delta_j;

                    if (new_refi >= 0 && new_refi < height && new_refj >= 0  && new_refj < width) // Only if valid pixel
                    {
                        // Add all the pixels surrounding the current pixel
                        sum[0] += image[new_refi][new_refj].rgbtBlue;
                        sum[1] += image[new_refi][new_refj].rgbtGreen;
                        sum[2] += image[new_refi][new_refj].rgbtRed;
                        divider++; // how many pixels have we added
                    }
                }
            }
            // Insert blurred pixels into image copy.
            image_copy[i][j].rgbtBlue = round((float) sum[0] / divider);
            image_copy[i][j].rgbtGreen = round((float) sum[1] / divider);
            image_copy[i][j].rgbtRed = round((float) sum[2] / divider);

            // Reset the pixel sum
            for (int m = 0; m <= 2; m++)
            {
                sum[m] = 0;
            }
            // reset pixel counter
            divider = 0;
        }
    }

    // Transfer back blurred pixels to original image
    for (int k = 0; k < height; k++)
    {
        for (int l = 0; l < width; l++)
        {
            image[k][l] = image_copy[k][l];
        }
    }


    return;
}
