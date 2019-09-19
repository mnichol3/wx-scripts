# GOES-R Series Advanced Baseline Imagery (ABI) Channels, Scans, & Products

## ABI Scan Sectors

Scan Sector | Description | Files/day/satellite/channel by mode
--------------|---------------|-----------------------------------
C | Continental U.S. (CONUS) Scan | 288 (Modes 3, 4, 6)
F | Full Disk Scan | 96 (Mode 3), 288 (Mode 4), 144 (Mode 6)
M1 | Mesoscale Region #1 | 1440 (in Mode 3 only)
M2 | Mesoscale Region #2 | 1440 (in Mode 3 only)

## ABI Scan Modes
Scan Mode | Description
-------------|------------
M3, M6 | Mode 3 or 6 (mostly in effect, includes meso)
M4 | Mode 4 (Full Disk scans every 5 mins, no meso scans)

## ABI Channels
ABI Channel | Central Wavelength (um)| Nominal Resolution (km) | Channel Type | Uses
---------------|------------------------|-----------------------------|----------------|--------
C01 | 0.47 | 1 | Blue | Visible
C02 | 0.64 | 0.5 | Red | Visible
C03 | 0.86 | 1 | Veggie | Near-IR
C04 | 1.37 | 2 | Cirrus | Near-IR
C05 | 1.6 | 2 | Snow/Ice | Near-IR
C06 | 2.2 | 2 | Cloud Particle Size | Near-IR
C07 | 3.9 | 2 | Shortwave Window | Near-IR
C08 | 6.2 | 2 | Upper-Level Tropospheric Water Vapor | IR
C09 | 6.9 | 2 | Mid-Level Tropospheric Water Vapor | IR
C10 | 7.3 | 2 | Lower-Level Tropospheric Water Vapor | IR
C11 | 8.4 | 2 | Cloud-Top Phase | IR
C12 | 9.6 | 2 | Ozone | IR
C13 | 10.3 | 2 | "Clean" Longwave Window | IR
C14 | 11.2 | 2 | Longwave Window | IR
C15 | 12.3 | 2 | "Dirty" Longwave Window | IR
C16 | 13.3 | 2 | "CO2" Longwave Window | IR

## ABI L1b and L2+ Products*
Data Type Name | Description | ABI Channel | ABI Scan Sector | ABI Scan Mode | Satellite
------------------- | --------------|---------------|--------------------|-------------------|--------
RAD | ABI L1b Radiances | C01 - C16 | M1, M2, C, F | 3, 4, 6 | G16, G17
CMIP | ABI L2+ Cloud and Moisture Imagery (single-band) | C01 - C16 | M1, M2, C, F | 3, 4, 6 | G16, G17
FDC | ABI L2+ Fire/Hot Spot Characterization | N/A | C, F | 3, 4, 6 | G16, G17
MCMIP | ABI L2+ Cloud and Moisture Imagery (multi-band) | N/A | M1, M2, C, F | 3, 4, 6 | G16, G17

#####  *This is not an exhaustive list & includes only those currently available on AWS
[Source](http://ncdc.noaa.gov/data-access/satellite-data/goes-r-series-satellites/glossary)
