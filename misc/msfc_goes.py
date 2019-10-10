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



def renum_images(dir_path, img_num_key):
    """
    Adds a padding zero to the image number in the file names of the downloaded MSFC
    imagery to aid in sorting

    Parameters
    ----------
    dir_path : str
        Path of the directory holding the image files
    img_num_re : str
        Regex expression to determine the image number from the file name

    Returns
    -------
    None
    """
    re_dict = {0: r'(\d{1,2}).jpg$',
               1: r'\d(\d{1,2}).jpg$'
    }

    img_num_re = re_dict[img_num_key]

    img_num_re = re.compile(img_num_re)

    for f in os.listdir(dir_path):
        if (f.split('.') != 'txt'):           # ignore text file holding filenames
            match = img_num_re.search(f)      # Get the image number from the file name

            if (match):
                img_num = match.group(1)

                # Add padding zero to image number if applicable
                new_img_num = img_num.zfill(2)

                # Construct the original absolute path for the image file
                dir_old = os.path.join(dir_path, f)

                # Replace original image number with new padded image number
                new_fname = 'image-{}.jpg'.format(new_img_num)
                # new_fname = f.replace(img_num, new_img_num)

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
    num_check_re = re.compile(r'(\d{2}).jpg$')
    base_path = os.path.split(f_path)[0]

    with open(f_path, 'r') as fh:
        reader = csv.reader(fh)
        fname_list = list(reader)[0]    # The list is returned as a 1-element list

    fname_list = [x.replace("'", "") for x in fname_list]

    new_path = os.path.join(base_path, 'formatted_fnames.txt')
    with open(new_path, 'w') as new_fh:
        for fname in fname_list:
            new_fh.write('{}\n'.format(fname))

    # Search the first filename (image number 1) to see if the last char in the
    # filename before the image number is also an integer
    # Ex: GANIMEHyPM61.jpg --> image number 1, but the last char in the filename is 6
    test_str = fname_list[0]
    match = num_check_re.search(test_str)

    if (match):
        # The last char in the filename IS an integer, so the regex used to
        # determine the image number must look for a 2-3 digit image number
        # img_num_re = r'(\d{2,3}).jpg$'
        img_num_re = 1
    else:
        # Last char in the filename isn't an int, so regex only needs to look
        # for a 1-2 digit image number in the filename
        # img_num_re = r'(\d{1,2}).jpg$'
        img_num_re = 0

    return (new_path, img_num_re)



def main():
    parser = create_parser()
    args = parser.parse_args()

    # Format the filename text file and determine the appropriate image number
    # regex expression based off the dynamic filename format
    formatted_fnames, img_num_re = preprocess_fnames(args.img_fnames)

    # Download the images from NASA MSFC if the '-d' argument is passed
    if (args.download):
        fetch_imgs(formatted_fnames, args.out_dir)

    # Renumber the downloaded image files
    renum_images(args.out_dir, img_num_re)

    # Get a sorted list of image filenames
    sorted_fnames = sort_files(args.out_dir)
    for f in sorted_fnames:
        print(f)


if __name__ == '__main__':
    main()
