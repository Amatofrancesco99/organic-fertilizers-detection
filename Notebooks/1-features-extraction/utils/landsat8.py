import ee, pandas as pd


def get_all_bands(image, date, polygon):
    '''
    Calculate all the Landsat-8 bands mean values for a specific date and polygon in a Landsat-8 image collection.

    Spectral bands in Landsat-8 refer to specific ranges of electromagnetic radiation (EMR) that are utilized in remote
    sensing applications to gather information about the Earth's surface. These bands are defined based on their wavelength 
    or frequency and are organized into various groups according to their spectral characteristics, including visible, 
    near-infrared, shortwave infrared, and thermal infrared.
    Each spectral band in Landsat-8 offers distinct insights into the reflectance and absorption properties of features
    on the Earth's surface. For instance, visible bands are particularly sensitive to the reflectance of green vegetation,
    water, and soil. Near-infrared bands are capable of detecting the reflectance of healthy vegetation. Shortwave infrared
    bands enable the detection of variations in moisture content and mineralogy, while thermal infrared bands can capture
    heat signatures.

    Args:
        image (ee.ImageCollection): The Landsat 8 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Returns the list of mean bands values
    bands_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11']
    bands_means = {}
    for band in bands_list:
        bands_means[band] = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[band]
    return bands_means