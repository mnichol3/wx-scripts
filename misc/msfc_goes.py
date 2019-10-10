parse_desc = """ Download GOES-16 loop images from NASA MSFC
(weather.msfc.nasa.gov)

Example usage:

> python msfc_goes.py -d -i /path/to/filenames.txt -o /path/to/dir
This will download the images specified in filenames.txt to the directory
specified by /path/to/dir

IMPORTANT!!!
Must be used quickly after obtaining the list of image filenames as the images
aren't saved on the server for long

Author: Matt Nicholson
"""
import os
import re
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
                        action=action='store_true')

    return parser



def renum_images(dir_path):
    """
    Adds a padding zero to the image number in the file names of the downloaded MSFC
    imagery to aid in sorting

    Parameters
    ----------
    dir_path : str
        Path of the directory holding the image files

    Returns
    -------
    None
    """
    fname_re = re.compile(r'(\d{1,2}).jpg$')

    for f in os.listdir(dir_path):
        if (f.split('.') != 'txt'):         # ignore text file holding filenames
            match = fname_re.search(f)      # Get the image number from the file name

            if (match):
                img_num = match.group(1)

                # Add padding zero to image number if applicable
                new_img_num = img_num.zfill(2)

                # Construct the original absolute path for the image file
                dir_old = os.path.join(dir_path, f)

                # Replace original image number with new padded image number
                new_fname = f.replace(img_num, new_img_num)

                # Construct the new abs path
                dir_new = os.path.join(dir_path, new_fname)

                # Rename the image file
                shutil.move(dir_old, dir_new)

                print('{} renamed as {}'.format(f, new_fname))



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



def main():
    parser = create_parser()
    args = parser.parse_args()

    # Download the images from NASA MSFC if the '-d' argument is passed
    if (args.download):
        fetch_imgs(args.img_fnames, args.out_dir)

    # Renumber the downloaded image files
    renum_images(args.out_dir)

    # Get a sorted list of image filenames
    sorted_fnames = sort_files(args.out_dir)
    for f in sorted_fnames:
        print(f)


if __name__ == '__main__':
    main()
