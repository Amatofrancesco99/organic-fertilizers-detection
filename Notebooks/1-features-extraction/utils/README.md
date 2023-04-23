# sentinel-satellites

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/Amatofrancesco99/master-thesis/blob/main/Notebooks/1-features-extraction/utils/LICENSE)
![maintained](https://img.shields.io/badge/maintained%3F-YES-green.svg)
![stars](https://img.shields.io/github/stars/Amatofrancesco99/master-thesis.svg)

This library provides an **easy-to-use**, **comprehensive**, and **flexible** way to work with satellites data from the Sentinel-1 and Sentinel-2 satellites. Its key advantages include: a **well-documented** API, **support** for the mainly used satellites, **open-source code**, and **regular updates**.<br>
In addition to the already mentioned advantages, the implemented code also **exploits machine parallelism** (designed to work efficiently with large volumes of data, allowing for faster processing times and improved performances) and **relies on Google Earth Engine (GEE) APIs** (used to access satellites data and perform some tasks such as *cloud masking*, *image compositing*, and *time series selection*).

These advantages make it an excellent tool for anyone working with satellites data, since it allows to *generate datasets that can be both easily used for data analysis and efficiently integrated with well-known ML libraries, to deploy models*.

**How to install it?**
```bash
$ pip install sentinel-satellites
```

This library is composed of lot of functions, the main ones are here described.

*** 
***
## `get_features()` function

It allows to get from an [input pandas DataFrame](#input-dataframe) composed of fields information, [an output DataFrame](#output-dataframe) that contains for each time [selected satellites](#how-to-execute-it) (sentinel-1 or sentinel-2) passed over the specified fields, within a given time period, all the mean values of some of the most used indexes (optical or radar).<br>
Please consider the [modifications](#whats-new) for indexes values assessment, starting from version `0.0.9` (reduced extraction time at the cost of making approximation).<br>

The `filters_params` parameter is a list containing the values of the Earth Engine filters to be used for extracting Image Collections, with the specified sentinel satellites. For Sentinel-2 the first parameter in the list is the value of the `CLOUDY_PIXEL_PERCENTAGE` filter (`LESS OR EQUAL TO` - values in range `[0, 100]`), whereas for Sentinel-1 the first parameter in the list is the value of the `orbitProperties_pass` filter (`ASCENDING` or `DESCENDING`).

The `fields_threads` parameter is the number of threads to dedicate to parallelization over the fields level, the remaining part instead is used to apply parallelization over dates level. The value of this parameter should be high (with respect to the overall number of threads exploitable - see your computer specifications) if you have a lot of fields but a little time-span to consider, whereas if you have fewer fields but a bigger time-span you should decrease this parameter. Finally, if you have lot of fields with lot of dates to process it should may be optimal considering half of the overall number of threads available. <br>A correct choice of this parameter can drastically reduce the features extraction time.

See the [code](https://github.com/Amatofrancesco99/master-thesis/blob/main/Notebooks/1-features-extraction/utils/sentinel_satellites.py) for a better understanding.

## Input DataFrame
The input DataFrame, lets suppose named `fields_df`, should be structured as follows (just columns position matters):

| field_name      |              polygon_coordinates                  |
|-----------------|---------------------------------------------------|
| P-BLD           |  [(-4.202723286616649, 43.39683579015289), (-4...]|
| P-BLLT1         | [(-4.085622203603083, 43.429605845026266), (-4...]|
| P-BLLT2         | [(-4.084840437376829, 43.430826294936246), (-4...]|
| P-CBRCS1        | [(-4.200826431306206, 43.39067464298489), (-4....]|
| ...             |             ...                                   |
| P-VNS 	      | [(-4.151167740565273, 43.40535762666503), (-4....]|


## How to execute it?

First you have to initialize and authorize the Google Earth Engine APIs.

```python
import ee, sentinel_satellites

ee.Authenticate()
ee.Initialize()
```

Then, supposing that you have already loaded the `fields_df` pandas DataFrame, you have just to run the following code. Change the `sentinel` number, in case you want sentinel `1` indexes extracted for the fields specified (within the time period selected - be careful that the given date format is consistent with [ISO 8601](https://it.wikipedia.org/wiki/ISO_8601) notation). See the above [general description](#get_features-function), instead, to comprehend what `filters_params` and `fields_threads` parameters are useful for.

```python
df = sentinel_satellites.get_features(fields_df, "2022-01-01", "2022-12-31", sentinel=2, filters_params=['40'], fields_threads=3)
```

## Output DataFrame
The output generated DataFrame, namely `df`, will be structured as follows:
| field_name | s2_acquisition_date | B1 | B2 | B3 | ... | MCARI2 | BSI | GLI | ALTERATION | SDI |
|------------|---------------------|----|----|----|-----|--------|-----|-----|------------|-----|
P-BLD | 2022-01-06 | 2.260204    | 119.981293  | 550.044218  | ...  | 0.922907 | 6282.955014  | 0.513069 | 2.131255 | 3484.508503 |
P-BLD | 2022-01-16 | 13.785714   | 111.540816  | 528.481293  | ...  | 0.921371 | 6545.200602  | 0.517949 | 2.127614 | 3636.382653 |
...   | ...        | ...         | ...         |	...	     | ...  | ...      | ...          | ...      | ...      | ... | ...   |
P-VNS | 2022-11-17 | 1133.057399 | 1364.994619 | 1726.755157 | .... | 0.594553 | 11195.020251 |	0.070841 | 1.441033 | 1939.695067 |
P-VNS | 2022-12-17 | 955.040359  | 1208.792825 | 1617.324664 | ...  | 0.688394 | 10547.592756 |	0.107797 | 1.505526 | 2913.218834 |


***
***
## What's new?
* `version: 0.0.5`:
    * Code refactoring and improved descriptions
    * Now, in `get_features()` function, column names in the passed pandas DataFrame that contains field name and coordinates does not matter (just column position matters)
    * Added new optical indexes
    * Fixed bug case occurring when `fields_df` has just one field inside
    * Improving parallelization. Now each thread does not only work on gathering all features for a single field, but also on computing them on dates chunks

* `version: 0.0.6`:
    * Code refactoring and improved descriptions
    * Fixed issues in calling `radar_features` functions and other minor bugs
    * Added new radar indexes
    * Reduced the `CLOUDY_PIXEL_PERCENTAGE` parameter to `25` (for optical indexes extraction)
    * The output DataFrame is now ordered by the first two columns (`field_name` & `acquisition_date`), in ascending order 

* `version: 0.0.7`, `0.0.8` & `0.0.9`:
    * Fixed `EOMI3` formula
    * Improved parallelization in `get_features()` function by calculating all the radar and optical indexes using mean bands/polarizations values (this allowed to drastically reduce the number of queries to Google Earth Engine via APIs) <br>
    *E.G:* `NDVI mean = (NIR mean - RED mean) / (NIR mean + RED mean)` <br>
    Please note that this modification leds to an approximation of the various indexes, which cannot be neglected for some particular applications (e.g. precision agriculture)
    * Adjusted descriptions and fixed all `optical_features` and `radar_features` functions, such that now are working directly on mean bands values (relative to a field of interest in a single date)
    * Added EE filters and allowed users to specify the list of parameters values to be used for filters to extract Sentinel Images Collections

* `version: 0.0.10`, `0.0.11`, `0.0.12` & `0.0.13` (current):
    * Improved descriptions and fixed broken links due to code refactoring
    * Added `.reset_index(drop=True)` method when return the extracted indexes DataFrame