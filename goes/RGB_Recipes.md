# GOES-R Series Advanced Baseline Imager (ABI) RGB Product Recipes


## Air Mass RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 6.2 - 7.3 | -26.2 to 0.6 C | 1 | Vertical water vapor difference | Moist upper levels | Dry upper levels
Green | 9.6 - 10.3 | -43.2 to 6.7 C  | 1 | Tropopause height based on ozone | Low trop & high ozone | High trop & low ozone
Blue | 6.2 (inverted) | -29.25 to -64.65 C  | 1 | Upper-level water vapor (~200-500 mb) | Dry upper levels | Moist upper levels
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/QuickGuide_GOESR_AirMassRGB_final.pdf)


## CIMSS Natural True Color RGB
Color | Band 
-------|-----------
Red | 0.64
Green | 0.45*Red + 0.1*Veggie + 0.45*Blue
Blue | 0.47
[Source](http://cimss.ssec.wisc.edu/goes/OCLOFactSheetPDFs/ABIQuickGuide_CIMSSRGB_v2.pdf)

## Day Cloud Convection RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 0.64 | 0 to 100% | 1.7 | Reflectance of clouds & surfaces | Water, vegetation, land | Cloud, snow, white sand
Green | 0.64 | 0 to 100% | 1.7 | Reflectance of clouds & surfaces | Water, vegetation, land | Cloud, snow, white sand
Blue | 10.3 | 49.85 to -70.15 C | 1 |  Surface or cloud top temperature | Warm: land (seasonal), ocean | Cold: land (winter), snow, high clouds
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/QuickGuide_DayCloudConvectionRGB_final.pdf)

## Day Land Cloud RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 1.6 | 0 to 97.5% | 1 | Reflectance of clouds & surfaces | Ice or large particle clouds, water, snow/ice, sea ice | Water clouds with small drops, and desert
Green | 0.86 | 0 to 108.6% | 1 | Reflectance of clouds & surfaces | Water, inactive vegetation, base soil | Clouds, vegetation, and snow/ice
Blue | 0.64 | 0 to 100.0 % | 1 |  Reflectance of clouds & surfaces | Thin cloud, water, vegetation, bare soil | Thick clouds and snow/ice
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/QuickGuide_GOESR_daylandcloudRGB_final.pdf)

## Day Land Cloud Fire RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 2.2 | 0 to 100% | 1 | Particle size/ land type | Large water/ice particles, water or snow | Small water/ice particles, hotspot
Green | 0.86 | 0 to 100%  | 1 | Reflectance of clouds & surfaces | Thin cloud, water, less green vegetation, bare soil | Thick cloud, highly vegetated, snow, desert
Blue | 0.64 | 0 to 100%  | 1 |  Reflectance of clouds & surfaces | Thin cloud, water, vegetation, bare soil | Thick cloud, snow, desert
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/QuickGuide_GOESR_DayLandCloudFireRGB_final.pdf)

# Differential Water Vapor RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 7.3 - 6.2 (inverted) | 30 to -3 C | 0.2587 | Vertical water vapor difference | Moist upper levels | Dry upper levels
Green | 7.3 (inverted) | 5 to -60 C  | 0.4 | Low-level water vapor | Dry lower levels | Moist lower levels
Blue | 6.2 (inverted) | -29.25 to -64.65 C  | 0.4 |  Upper-level water vapor (~200-500 mb) | Dry upper levels | Moist upper levels
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/QuickGuide_GOESR_DifferentialWaterVaporRGB_final.pdf)

## Dust RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 12.3 - 10.3 | -6.7 to 2.6 C | 1 | Optical depth / cloud thickness | Thin clouds | Thick clouds or dust
Green | 11.2 - 8.4 | -0.5 to 20 C | 2.5 | Particle phase | Ice and particles of uniform shape (dust) | Water particles or thin cirrus over deserts
Blue | 10.3 | -11.95 to 15.55 C | 1 | Surface temperature | Cold surface | Warm surface
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/Dust_RGB_Quick_Guide.pdf)

## Fire Temperature RGB
Color | Band / Band Diff. (um) | Min - Max | Gamma | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 3.9 | 0 to 60 C | 0.4 | Cloud top phase & temperature | Cold land surfaces, water, snow, clouds | Hot land surface (low fire temperature)
Green | 2.2 | 0 to 100& | 1 | Particle size/ land type | Large ice/water particles, snow, oceans | Small ice/water particles, medium fire temperature
Blue | 1.6 | 0 to 75% | 1 | Particle size/ land type | Ice cloud with large particles, snow, oceans | Water clouds, high fire temperature
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/Fire_Temperature_RGB.pdf)

## Simple Water Vapor RGB
Color | Band / Band Diff. (um) | Min - Max | Physically Relates to... | **Small** contribution to pixel indicates... | **Large** contribution to pixel indicates... 
-------|---------------------------|-------------|----------|---------------------------|--------------------------|--------------
Red | 10.3 (inverted) | 5.81 to -70.86 C | Cloud top or surface temperature | Shallow low-mid clouds | High and/or deep clouds
Green | 6.2 (inverted) | -30.48 to -58.49 C | Upper-level water vapor (~200-500 mb) | Relatively dry upper-level atmosphere | Relatively moist upper-level atmosphere
Blue | 7.3 (inverted) | -12.12 to -28.03 C | Lower-level water vapor | Relatively dry lower-level atmosphere | Relatively moist lower-level atmosphere
[Source](http://rammb.cira.colostate.edu/training/visit/quick_guides/Simple_Water_Vapor_RGB.pdf)
