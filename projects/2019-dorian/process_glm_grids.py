from os import listdir
from os.path import isfile, join



def untar(dir_path, dest_path):
    """
    Unpack a gzip TAR archive located in the 'dir_path' directory into the
    'dest_path' directory

    Parameters
    ----------
    dir_path : str
        Path of the directory holding the archived files
    dest_path : str
        Path of the directory to unpack the archived files into

    Returns
    -------
    unpacked_files : list of str
        List of absolute paths (including filenames) of the unpacked directories

    Dependencies
    ------------
    > shutil.unpack_archive (from shutil import unpack_archive)
    > os.listdir            (from os import listdir)
    > os.path.isfile        (from os.path import isfile)
    > os.path.join          (from os.path import join)

    Notes
    -----
    * IF the files are GLM FED files from the lightning.umd.edu server,
        they will not have a file extension and they must be passed to
        trim_header() before they can be read by netCDF4.Dataset()
    * The archive files are unzipped as folders, not individual files.
    """
    from shutil import unpack_archive
    # from os import listdir
    # from os.path import isfile, join
    unpacked_files = []

    for f_name in listdir(dir_path):
        f_parts = f_name.split('.')
        if (f_parts[1] == 'tgz'):
            print('Unpacking {} to {}'.format(f_name, dest_path))
            f_abs = join(dir_path, f_name)
            # dest_abs = join(dest_path, f_name)
            unpack_archive(f_abs, dest_path, 'gztar')
            unpacked_files.append(join(dest_path, f_parts[0]))
    return unpacked_files



def trim_header(abs_path):
    """
    Trim the header off AWIPS-compatable GLM files and convert to netCDF. Not
    needed for files obtained from AWS

    Parameters
    ----------
    abs_path : str
        Absolute path of the file to read

    Returns
    -------
    abs_path : str
        Absolute path of the new file

    Dependencies
    ------------
    > os.path.isfile
    """
    from os import remove

    if (not isfile(abs_path)):
        raise OSError('File does not exist:', abs_path)

    if (not isfile(abs_path + '.nc') and abs_path.split('.')[-1] != 'nc'):

        print('Trimming {}'.format(abs_path.split('/')[-1]))

        with open(abs_path, 'rb') as f_in:
            f_in.seek(21)
            data = f_in.read()
            f_in.close()
            f_in = None

        trimmed_fname = abs_path + '.nc'

        with open(trimmed_fname, 'wb') as f_out:
            f_out.write(data)
            f_out.close()
            f_out = None

        # Delete the untrimmed file from the directory
        remove(abs_path)

    return trimmed_fname



def trim_fed_files(parent_dir):
    fnames = []
    for d in listdir(parent_dir):
        curr_date = join(parent_dir, d)

        for f in listdir(curr_date):
            curr_f = join(curr_date, f)
            new_fname = trim_header(curr_f)
            fnames.append(new_fname)
    return fnames



src_dir = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/raw'
dest_dir = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc'

# unpacked = untar(src_dir, dest_dir)
fed_fnames = trim_fed_files(dest_dir)

for f in fed_fnames:
    print(f)
