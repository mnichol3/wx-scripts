parse_desc = """ Download GOES-16 loop images from NASA MSFC SPORT
(weather.msfc.nasa.gov)
https://weather.msfc.nasa.gov/cgi-bin/sportPublishData.pl?dataset=goeseastabiconus&product=10p35um

Example usage
--------------

This will download the images specified in filenames.txt to the directory
specified by /path/to/dir:
> python msfc_sport_goes.py -d -i /path/to/filenames.txt -o /path/to/dir

The following will process already-downloaded image files:
> python msfc_sport_goes.py -i /home/mnichol3/Pictures/wx/2019-10-10/2/f_names.txt -o /home/mnichol3/Pictures/wx/2019-10-10/2

IMPORTANT!!!
Must be used quickly after obtaining the list of image filenames as the images
aren't saved on the server for long

Author: Matt Nicholson
"""

"""
Input filename file format
---------------------------
Just copy the list of partial image paths & names from the
NASA/MSFC Interactive GOES Data Selector image loop html source

"""
import os
import re
import csv
import shutil
import subprocess
import argparse


def create_parser():
    parser = argparse.ArgumentParser(description=parse_desc)
    parser.add_argument('-i', '--img_fnames', metavar='image filenames',
                        required=True, dest='img_fnames', action='store')
    parser.add_argument('-o', '--output_dir', metavar='directory',
                        required=True, dest='out_dir', action='store')
    parser.add_argument('-d', '--download', required=False, dest='download',
                        action='store_true')

    return parser



def renum_images(dir_path, img_num=1):
    """
    Adds a padding zero to the image number in the file names of the downloaded MSFC
    imagery to aid in sorting

    Parameters
    ----------
    dir_path : str
        Path of the directory holding the image files
    img_num_re : int
        Number to start the image number count from. Default: 1

    Returns
    -------
    None
    """
    fnames = sort_files(dir_path)

    for f in fnames:

            # Add padding zero to image number if applicable
            new_img_num = str(img_num).zfill(3)

            # Construct the original absolute path for the image file
            dir_old = os.path.join(dir_path, f)

            # Replace original image number with new padded image number
            new_fname = 'image-{}.gif'.format(new_img_num)
            # new_fname = f.replace(img_num, new_img_num)

            # Construct the new abs path
            dir_new = os.path.join(dir_path, new_fname)

            # Rename the image file
            shutil.move(dir_old, dir_new)

            print('{} renamed as {}'.format(f.ljust(17), new_fname))

            img_num += 1




def fetch_imgs(fname_file, out_dir):
    """
    Download the image files using wget and a file containing the image
    names on the MSFC server

    Parameters
    ----------
    fname_file : str
        Absolute path, including filename, of the text file containing the
        names of the image files to download as they appear on the NASA MSFC
        server
    out_dir : str
        Path of the directory to download the images to

    Returns
    -------
    None
    """

    base_url = 'https://weather.msfc.nasa.gov'

    cmd = 'wget -B {0} -P {1} -i {2}'.format(base_url, out_dir, fname_file)

    out_bytes = subprocess.check_output(cmd.split())
    print(out_bytes)



def sort_files(dir_path):
    """
    Return a list of sorted image filenames

    Parameters
    ----------
    dir_path : str
        Path to the directory holding the image files

    Returns
    -------
    img_files : list of str
        Sorted list of image file names
    """
    img_files = [f for f in os.listdir(dir_path) if (f.split('.')[1] != 'txt')]
    img_files.sort()
    return img_files



def preprocess_fnames(f_path):
    """
    Determine the format of the image filenames. Sometimes the last char before
    the image number will be an integer, which messes up the sorting function

    Parameters
    ----------
    f_path : str
        Absolute path, including filename, of the text file containing the
        names of the image files to download as they appear on the NASA MSFC
        server

    Returns
    -------
    Tuple of str : (new_path, img_num_re)
        new_path : Absolute path of the file holding the formatted image filenames
        img_num_re : Appropriate egex expression for the MSFC imagery filename format
    """
    # fname_re = re.compile(r'src=\"(\S+.gif)\"')
    fname_re = re.compile(r'src=\"(\S+.gif)\";$')
    base_path = os.path.split(f_path)[0]

    with open(f_path, 'r') as fh:
        reader = csv.reader(fh)
        fname_list = list(reader)       # Returns a list of 1 element lists

    # Get the actual filename from the partial html string
    stripped_fnames = []
    for f in fname_list:
        print(f)
        match = fname_re.search(f[0])
        if (match):
            curr_fname = match.group(1)
            print(curr_fname)
            stripped_fnames.append(curr_fname)

    new_path = os.path.join(base_path, 'formatted_fnames.txt')
    with open(new_path, 'w') as new_fh:
        for fname in stripped_fnames:
            new_fh.write('{}\n'.format(fname))

    return new_path



def main():
    parser = create_parser()
    args = parser.parse_args()

    # Format the filename text file and determine the appropriate image number
    # regex expression based off the dynamic filename format
    formatted_fnames = preprocess_fnames(args.img_fnames)

    # from sys import exit
    # exit(0)
    # Download the images from NASA MSFC if the '-d' argument is passed
    if (args.download):
        fetch_imgs(formatted_fnames, args.out_dir)

    # Renumber the downloaded image files
    renum_images(args.out_dir)

    # Get a sorted list of image filenames
    sorted_fnames = sort_files(args.out_dir)
    for f in sorted_fnames:
        print(f)


if __name__ == '__main__':
    main()
