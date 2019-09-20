"""
Author: Matt Nicholson

Script to download Dorian GLM data using my goesaws package

"""
import goesawsinterface
import datetime



def calc_date_chunks(start, end):
    """
    Creates 6-hr time chunks

    Parameters
    ----------
    start : str
        Format: 'MM-DD-YYYY-HH:MM'
    end : str
        Format: 'MM-DD-YYYY-HH:MM'

    Returns
    --------
    chunks : list of tuples of (str, str)

    Dependencies
    -------------
    > datetime
    """
    chunks = []

    start = datetime.datetime.strptime(start, '%m-%d-%Y-%H:%M')
    prev = start
    end = datetime.datetime.strptime(end, '%m-%d-%Y-%H:%M')

    while (prev <= end):
        # Increment 6 hours
        curr = prev + datetime.timedelta(seconds=21600)

        chunks.append((prev.strftime('%m-%d-%Y-%H:%M'), curr.strftime('%m-%d-%Y-%H:%M')))
        prev = curr

    """
    Adjust the last tuple incase the time period doesnt divide evenly into
    6-hr periods

    Ex
    ---
    Unadjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-15:00')

    Adjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-13:00')

    """
    if (datetime.datetime.strptime(chunks[-1][1], '%m-%d-%Y-%H:%M') > end):
        chunks = chunks[:-1]
        prev = prev - datetime.timedelta(seconds=21600)
        chunks.append((prev.strftime('%m-%d-%Y-%H:%M'), end.strftime('%m-%d-%Y-%H:%M')))

    return chunks



def glm_dl(date_chunk, outpath=None, dl=False):
    """
    date_chunk : tuple of str
        Format: (start, end)
        Date string format: 'MM-DD-YYYY-HH:MM'
    outpath: str, optional
        Path to the directory in which to save the data. Must be passed if dl is
        True
    dl : Bool, optional
        Whether or not to download the files. Default is False
    """
    print('\nRetrieving GLM files for: {} to {}'.format(date_chunk[0], date_chunk[1]))
    print('--------------------------------------------------------------')

    # Create new GOES AWS interface object
    conn = goesawsinterface.GoesAWSInterface()

    imgs = conn.get_avail_images_in_range('goes16', 'glm', date_chunk[0], date_chunk[1])

    for img in imgs:
        print('{} --> {}'.format(img.scan_time, img.filename))

    if (dl and outpath):
        result = conn.download('goes16', imgs, outpath, keep_aws_folders=False, threads=6)
        for x in result._successfiles:
            print(x.filepath)



def main():
    """
    Dorian lifespan (the parts we actually care about):
    09-01-2019-16:00 to 09-06-2019-13:00
    """
    local_abi_path_inf = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/abi/inf'
    local_glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'

    start = '09-01-2019-15:00'
    end = '09-06-2019-13:00'

    time_chunks = calc_date_chunks(start, end)

    for chunk in time_chunks:
        glm_dl(chunk, outpath=local_glm_path, dl=True)



if __name__ == '__main__':
    main()
