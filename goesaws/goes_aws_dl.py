"""
Author: Matt Nicholson

Command line wrapper for the GOESAws package

Example usage
-------------

> python goes_aws_dl.py --sat 'goes16' -i 'abi' --start '09-01-2019-00:00' --end '09-01-2019-00:15' -p 'CMIP' --sector 'C' --chan '02'
> python goes_aws_dl.py --start '09-01-2019-00:00' --end '09-01-2019-00:15' -p 'CMIP' --sector 'M1' --chan '02'
> python goes_aws_dl.py --start '09-01-2019-00:00' --end '09-01-2019-00:15' -p 'CMIP' --sector 'M1' --chan '02' -dl -o 'path/to/download'
> python goes_aws_dl.py --start '09-01-2019-00:00' --end '09-01-2019-00:15' -p 'MCMIP' --sector 'C' -dl -o 'path/to/download'

GLM:
> python goes_aws_dl.py -i 'glm' --start '09-01-2019-16:00' --end '09-01-2019-16:30'
> python goes_aws_dl.py -i 'glm' --start '09-01-2019-16:00' --end '09-01-2019-16:30' -dl -o 'path/to/download'
"""

import argparse

import goesawsinterface

parse_desc = """A Package to download GOES-R series (GOES-16 & -17) from NOAA's
Amazon Web Service (AWS) bucket.
"""

def create_arg_parser():
    parser = argparse.ArgumentParser(description=parse_desc)

    # Satellite argument (goes16, goes17)
    # Not required. Default value is 'goes16'
    parser.add_argument('--sat', metavar='satellite', required=False,
                        dest='sat', default='goes16', action='store')

    # Instrument ('abi', 'glm')
    # Not required. Default value is 'abi'
    parser.add_argument('-i', '--instr', metavar='instrument', required=False,
                        dest='instr', action='store', type=str, default='abi',
                        help='Instrument/sensor')

    parser.add_argument('-p', '--prod', metavar='product', required=False,
                        dest='prod', action='store', type=str, default=None,
                        help='Sensor product, e.g., CMIP, MCMIP, ...')

    parser.add_argument('-c', '--chan', metavar='channel', required=False,
                        dest='channel', action='store', type=str, help='ABI Channel as a string',
                        default=None)

    parser.add_argument('-s', '--sector', metavar='scan sector', dest='sector',
                        action='store', type=str, default=None,
                        help='ABI scan sector, e.g., "C", "M1", "M2"')

    parser.add_argument('-o', '--output_dir', metavar='directory', dest='out_dir',
                        required=False, type=str, action='store', help='Directory to download files to')

    parser.add_argument('--start', metavar='start time', dest='start', required=True,
                        action='store', type=str, help='Start time')

    parser.add_argument('--end', metavar='end time', dest='end', required=True,
                        action='store', type=str, help='End time')

    parser.add_argument('-d', '--dl', dest='dl', default=False, action='store_true',
                        help='File download flag')

    return parser



def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    conn = goesawsinterface.GoesAWSInterface()

    imgs = conn.get_avail_images_in_range(args.sat, args.instr, args.start, args.end,
                                          product=args.prod, sector=args.sector,
                                          channel=args.channel)

    for img in imgs:
        print('{} --> {}'.format(img.scan_time, img.filename))

    if (args.dl and args.out_dir):
        result = conn.download('goes16', imgs, args.out_dir, keep_aws_folders=True, threads=6)

        for x in result._successfiles:
            print(x.filepath)



if __name__ == '__main__':
    main()
