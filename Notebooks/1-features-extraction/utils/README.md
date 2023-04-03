# sentinel-satellites 🌍

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/Amatofrancesco99/master-thesis/blob/main/Notebooks/1-features-extraction/utils/LICENSE)
![maintained](https://img.shields.io/badge/maintained%3F-YES-green.svg)
![stars](https://img.shields.io/github/stars/Amatofrancesco99/master-thesis.svg)

This library provides an **easy-to-use**, **comprehensive**, and **flexible** way to work with satellite data from the Sentinel-1 and Sentinel-2 satellites. Its key advantages include: a **well-documented** API, **support** for the mainly used satellites, **open-source code**, and **regular updates**.<br>
In addition to the already mentioned advantages, the implemented code also **exploits machine parallelism** (designed to work efficiently with large volumes of data, allowing for faster processing times and improved performances) and **relies on Google Earth Engine (GEE) APIs** (used to access satellites data and perform some tasks such as *cloud masking*, *image compositing*, and *time series selection*).

These advantages make it an excellent tool for anyone working with satellite data, since it allows to *generate datasets that can be both easily used for data analysis and efficiently integrated with well-known ML libraries, to deploy models*.

**How to install it?**
```bash
$ pip install sentinel-satellites
```

This library is composed of lot of functions, the main ones are here described.

*** 
***
## `get_features()` function

It allows to get from a pandas DataFrame composed of crop fields information, another DataFrame that contains for each time a satellite (sentinel-1 or sentinel-2) passed on regions of interest, within a given time period, all the mainly used features mean values (optical or radar).
Have a look at: [input DataFrame](#input-dataframe), [execution example](#how-to-execute-it) and [generated DataFrame](#output-dataframe).

The `filters_params` parameter is a list containing the values of the Earth Engine filters to be used for extracting Image Collections, with the specified sentinel satellite. For Sentinel-2 the first parameter in the list is the value of the `CLOUDY_PIXEL_PERCENTAGE` filter (`LESS OR EQUAL TO` - values in range `[0, 100]`), whereas for Sentinel-1 the first parameter in the list is the value of the `orbitProperties_pass` filter (`ASCENDING` or `DESCENDING`).

The `fields_threads` parameter is the number of threads to dedicate to parallelization over the fields level, the remaining part instead is used to apply parallelization over dates level. The value of this parameter should be high (with respect to the overall number of threads exploitable - see your computer specifications) if you have a lot of crop fields but a little time-span to consider, whereas if you have fewer fields but a bigger time-span you should decrease this parameter. Finally, if you have lot of fields with lot of dates to process it should may be optimal considering half of the overall number of threads available. <br>A correct choice of this parameter can drastically reduce the features extraction time.

See the [code](https://github.com/Amatofrancesco99/master-thesis/blob/main/Notebooks/1-features-extraction/utils/sentinel_satellites.py) for a better understanding.

## Input DataFrame
The input DataFrame, lets suppose named `fields_df`, should be structured as follows (just columns position matters):

| crop_field_name |              polygon_coordinates                  |
|-----------------|---------------------------------------------------|
| P-BLD           |  [(-4.202723286616649, 43.39683579015289), (-4...]|
| P-BLLT1         | [(-4.085622203603083, 43.429605845026266), (-4...]|
| P-BLLT2         | [(-4.084840437376829, 43.430826294936246), (-4...]|
| P-CBRCS1        | [(-4.200826431306206, 43.39067464298489), (-4....]|
| ...             |             ...                                   |


## How to execute it?

First you have to initialize and authorize the Google Earth Engine APIs.

```python
import ee, sentinel_satellites

ee.Authenticate()
ee.Initialize()
```

Then, supposing that you have already loaded the `fields_df` pandas DataFrame, you have just to run the following code. Change the `sentinel` number, in case you want sentinel `1` features extracted for the crop fields specified (within the time period selected - be careful that the given date format is consistent with [ISO 8601](https://it.wikipedia.org/wiki/ISO_8601) notation). See the above [general description](#get_features-function), instead, to comprehend what `filters_params` and `fields_threads` parameters are useful for.

```python
df = sentinel_satellites.get_features(fields_df, "2022-01-01", "2022-12-31", sentinel=2, filters_params=['40'], fields_threads=3)
```

## Output DataFrame
The output generated DataFrame, namely `df`, will be structured as follows:
| crop_field_name | s2_acquisition_date | NDVI      | EOMI1     | EOMI2     | EOMI3     | EOMI4     | NBR2      | SAVI      | MSAVI     | ...   |
|----------------|---------------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|----------------|
P-BLD | 2022-01-06 | 0.729366 | -0.376095 | 0.220854 | -0.090378 |	0.504886 | 0.324869	| 0.941383 | 0.839771 |	... |
P-BLD | 2022-01-16	| 0.760237 | -0.338848 | 0.316256 | -0.060777 | 0.569916 | 	0.316494 | 0.885469 | 0.861267 | ... |
P-BLD | 2022-01-26 | 0.452795 | -0.198903 | 0.123193 |	0.202623 | 0.286175 | 0.169172 | 0.646540 |	0.618500 | ... |
... | ... | ... | ... |	...	 | ... | ... | ... | ... | ... | ... | ...|
P-VG2 |	2022-11-12 | 0.393333 | -0.133609 |	0.163594 | 0.268466 | 0.304470 | 0.148289 |	0.561634 | 0.562339 | ... |
P-VG2 | 2022-11-17 | 0.308817 |	-0.158042 | 0.078185 | 0.292526 | 0.177674 | 0.100908 |	0.440931 | 0.470664 | ... |
P-VG2 | 2022-12-05 | 0.646324 |	-0.349386 | 0.188256 | 0.010998 | 0.373301 | 0.199133 |	0.922892 | 0.784226 | ... |


***
***
## What's new?
* `version: 0.0.5`:
    * Code refactoring and improved descriptions
    * Now, in `get_features()` function, column names in the passed pandas DataFrame that contains field name and coordinates does not matter (just column position matters)
    * Added new optical features
    * Fixed bug case occurring when `fields_df` has just one field inside
    * Improving parallelization. Now each thread does not only work on gathering all features for a single field, but also on computing them on dates chunks

* `version: 0.0.6`:
    * Code refactoring and improved descriptions
    * Fixed issues in calling `radar_features` functions and other minor bugs
    * Added new radar features
    * Reduced the `CLOUDY_PIXEL_PERCENTAGE` parameter to `25` (for optical features extraction)
    * The output DataFrame is now ordered by the first two columns (`field_name` & `acquisition_date`), in ascending order 

* `version: 0.0.7`:
    * Fixed `EOMI3` formula

* `versions: 0.0.8` & `0.0.9`:
    * Improved parallelization in `get_features()` function by calculating all the radar and optical features using mean bands/polarizations values (this allowed to drastically reduce the number of queries to Google Earth Engine via APIs)
    *E.G:* `NDVI mean = (NIR mean - RED mean) / (NIR mean + RED mean)`
    * Adjusted descriptions and fixed all `optical_features` and `radar_features` functions, such that now are working directly on mean bands values (relative to a crop field of interest in a single date)
    * Added EE filters and allowed users to specify the list of parameters values to be used for filters to extract Sentinel Images Collections

* `version: 0.0.10` (current):
    * Improved descriptions and fixed broken links due to code refactoring