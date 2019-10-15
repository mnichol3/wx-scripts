import matplotlib.pyplot as plt
import pyart
from os.path import join

DATA_PATH = '/media/mnichol3/pmeyers1/MattNicholson/nexrad'

fname = 'KAMA20190523_210747_V06'
fpath = join(DATA_PATH, fname)

radar = pyart.io.read(fpath)
xsect = pyart.util.cross_section_ppi(radar, [35.09])

display = pyart.graph.RadarDisplay(xsect)
fig = plt.figure()
display.plot('reflectivity', 0, vmin=-32, vmax=84.)
plt.axis([0, 100, 0, 40])
plt.tight_layout()
plt.show()
