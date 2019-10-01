import goesawsinterface

# Path to the directory that you want to save the files in
# local_abi_path = '/media/mnichol3/tsb1/data/abi'
# local_abi_path = '/media/mnichol3/tsb1/data/abi/dorian/inf'
local_abi_path = '/media/mnichol3/pmeyers1/MattNicholson/abi'

# Create a connection object
conn = goesawsinterface.GoesAWSInterface()

# Returns a list of AwsGoesFile objects representing AWS
                                               # product      # start date       # end date     # sector  # channel
# imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-01-2019-00:00', '09-06-2019-13:00', product='ABI-L2-CMIP', sector='M1', channel='13')
# imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-01-2019-00:00', '09-06-2019-13:00', product='ABI-L1b-Rad', sector='M1', channel='02')
# imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-01-2019-13:00', '09-01-2019-13:10', product='Rad', sector='M1', channel='02')
# imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-01-2019-13:00', '09-01-2019-13:10', product='MCMIP', sector='M1', channel=None)
# imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-16-2019-16:00', '09-16-2019-17:10', product='CMIP', sector='M1', channel='02')

# imgs = conn.get_avail_images_in_range('goes16', 'glm', '09-01-2019-16:00', '09-06-2019-13:00')
# imgs = conn.get_avail_images_in_range('goes16', 'glm', '09-01-2019-16:00', '09-01-2019-16:30')
imgs = conn.get_avail_images_in_range('goes16', 'abi', '09-30-2019-12:00', '09-30-2019-20:00', product='MCMIP', sector='C')#, channel=None)

for img in imgs:
    print('{} --> {}'.format(img.scan_time, img.filename))
    # print(img.shortfname)

result = conn.download('goes16', imgs, local_abi_path, keep_aws_folders=False, threads=6)
# for x in result._successfiles:
#     print(x.filepath)
