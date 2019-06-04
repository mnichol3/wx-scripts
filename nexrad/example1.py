import matplotlib.pyplot as plt
from datetime import datetime
import pyart
import aws_viewer

conn = aws_viewer.conn

out_path = '/media/mnichol3/pmeyers1/MattNicholson/nexrad'

#aws_viewer.avail_scans(conn, '23', '05', '2019', 'KAMA')

scans = aws_viewer.get_scans_start_end(conn, '23', '05', '2019', 'KAMA', '21', '0', '22', '0')
results = aws_viewer.download_files(conn, scans[0:4], out_path)


fig = plt.figure(figsize=(16,12))
for i,scan in enumerate(results.iter_success(),start=1):
    ax = fig.add_subplot(2,2,i)
    radar = scan.open_pyart()
    display = pyart.graph.RadarDisplay(radar)
    display.plot('reflectivity',0,ax=ax,title="{} {}".format(scan.radar_id,scan.scan_time))
    display.set_limits((-150, 150), (-150, 150), ax=ax)

plt.show()
