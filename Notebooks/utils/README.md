# sentinel-satellites 🌍

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)
![maintained](https://img.shields.io/badge/maintained%3F-YES-green.svg)
![stars](https://img.shields.io/github/stars/Amatofrancesco99/master-thesis.svg)

A Python library that allows to extract data from sentinel satellites, exploiting machine parallelism and relying on Google Earth Engine APIs.
How to install it?

```bash
$ pip install sentinel-satellites
```

This library is composed of some main functions, each of them is described in this README.

*** 
***
## get_features() function

The ```get_features()``` function allows to get from a pandas DataFrame composed of crop fields information, a start date, an end date, and a sentinel integer as inputs. It returns a pandas DataFrame of calculated indices for each field and acquisition date within the specified date range, using the selected sentinel satellite.

Furthermore, it works in parallel in order to exploit the entire computational power of the machine on which you are running this function (load balanced the work of each core).

Please consider that, for usability reasons some filters have been fixed (like the pixel cloudy percentage, and other things). See the [code](sentinel_satellites.py) for having a better understanding.

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

Then, supposing you have already loaded the `fields_df` pandas DataFrame you have just to run the following code. You can change the `sentinel ID`, in case you want to get the sentinel `1` features extracted for the crop fields specified (within the time period selected).

```python
df = sentinel_satellites.get_features(fields_df, "2022-01-01", "2022-12-31", sentinel=2)
```

## Output DataFrame
The output generated DataFrame, namely `df`, will be structured as follows:
| crop_field_name | s2_acquisition_date | NDVI      | EOMI1     | EOMI2     | EOMI3     | EOMI4     | NBR2      | SAVI      | MSAVI     | ...   |
|----------------|---------------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|----------------|
P-FNFR | 2022-01-06 | 0.729366 | -0.376095 | 0.220854 | -0.090378 |	0.504886 | 0.324869	| 1.041383 | 0.839771 |	... |
P-FNFR | 2022-01-16	| 0.760237 | -0.338848 | 0.316256 | -0.060777 | 0.569916 | 	0.316494 | 1.085469 | 0.861267 | ... |
P-FNFR | 2022-01-26 | 0.452795 | -0.198903 | 0.123193 |	0.202623 | 0.286175 | 0.169172 | 0.646540 |	0.618500 | ... |
... | ... | ... | ... |	...	 | ... | ... | ... | ... | ... | ... | ...|
P-VG2 |	2022-11-12 | 0.393333 | -0.133609 |	0.163594 | 0.268466 | 0.304470 | 0.148289 |	0.561634 | 0.562339 | ... |
P-VG2 | 2022-11-17 | 0.308817 |	-0.158042 | 0.078185 | 0.292526 | 0.177674 | 0.100908 |	0.440931 | 0.470664 | ... |
P-VG2 | 2022-12-05 | 0.646324 |	-0.349386 | 0.188256 | 0.010998 | 0.373301 | 0.199133 |	0.922892 | 0.784226 | ... |


***
***
## What's new (`version: 0.0.5`)?
* Refactoring code in `get_features()` function, such that column names in the passed pandas DataFrame that contains field name and coordinates does not matter (just column position matters)
* Added a lot of optical features
* Fixed bug case occurring when `fields_df` has just one field inside