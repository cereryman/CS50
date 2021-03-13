#include "helpers.h"

#include <math.h>
#include  <stdio.h>

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

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{

    RGBTRIPLE image_copy[height][width];

    int new_refi, new_refj, g_refi, g_refj, gx_gain, gy_gain;
    long double g[3]  = {0, 0, 0}; // Index = 0 Green, Index = 1 Blue, Index = 2 Red
    int gx[3] = {0, 0, 0}; // Index = 0 Green, Index = 1 Blue, Index = 2 Red
    int gy[3] = {0, 0, 0}; // Index = 0 Green, Index = 1 Blue, Index = 2 Red

    const int gx_matrix[3][3] =
    {
        { -1, 0, 1}, /*  initializers for row indexed by 0 */
        { -2, 0, 2}, /*  initializers for row indexed by 1 */
        { -1, 0, 1}, /*  initializers for row indexed by 2 */
    };

    const int gy_matrix[3][3] =
    {
        { -1, -2, -1}, /*  initializers for row indexed by 0 */
        {  0,  0,  0}, /*  initializers for row indexed by 1 */
        {  1,  2,  1}, /*  initializers for row indexed by 2 */
    };

    // Create a new image so that edge detection algorithm uses the original surrounding pixels and not the "filtered" ones.
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image_copy[i][j] = image[i][j];
        }
    }

    // To calculate Gx and Gy for the pixels; loop through the entire image
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

                    g_refi = delta_i + 1;
                    g_refj = delta_j + 1;

                    if ((new_refi >= 0 && new_refi < height) && (new_refj >= 0  && new_refj < width)) // Only if valid pixel (not along cd psetedge)
                    {
                        // Sum G_x values for each pixel
                        gx[0] += image[new_refi][new_refj].rgbtBlue * gx_matrix[g_refi][g_refj];
                        gx[1] += image[new_refi][new_refj].rgbtGreen * gx_matrix[g_refi][g_refj];
                        gx[2] += image[new_refi][new_refj].rgbtRed * gx_matrix[g_refi][g_refj];
                        // Sum G_y values for each pixel
                        gy[0] += image[new_refi][new_refj].rgbtBlue * gy_matrix[g_refi][g_refj];
                        gy[1] += image[new_refi][new_refj].rgbtGreen * gy_matrix[g_refi][g_refj];
                        gy[2] += image[new_refi][new_refj].rgbtRed * gy_matrix[g_refi][g_refj];
                    }
                }
            }

            // Calculate final G value
            for (int m = 0; m <= 2; m++)
            {
                g[m] = sqrt(pow(gx[m], 2) + pow(gy[m], 2));

                if (g[m] > 255)
                {
                    g[m] = 255;
                }
            }

            // Insert blurred pixels into image copy.
            image_copy[i][j].rgbtBlue = (int)round(g[0]);
            image_copy[i][j].rgbtGreen = (int)round(g[1]);
            image_copy[i][j].rgbtRed = (int)round(g[2]);

            // Reset the G values
            for (int m = 0; m <= 2; m++)
            {
                gx[m] = 0;
                gy[m] = 0;
            }
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