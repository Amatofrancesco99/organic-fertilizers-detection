import ee, pandas as pd


def calculate_bsi(image, date, polygon, type=""):
    """
    Calculate the BackScatter-Based Index (BSI), Polarimetric BackScatter-Based Index (PBSI),
    or Co-Polarized Polarimetric BackScatter-Based Index (CPBSI) for a specific date and polygon in a
    Sentinel-1 image collection.
    
    - BSI (BackScatter Difference Index) measures the difference between the backscatter signal of the radar images
      pre and post-fertilization. After fertilization, the electrical properties of the soil and plants can change, 
      affecting the amount of backscatter signal received by the radar.
    - PBSI (Polarimetric BackScatter Index) is an index that measures signal polarization of radar images backscatter.
    - CPBSI (Cross-bias channel BackScatter Index) is an index that measures the amount of backscatter signal received
      by the image cross polarization channel radar.

    Args:
        image (ee.ImageCollection): The Sentinel-1 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        type (str): The type of BSI to calculate: 'BSI' (default), 'P' or 'CP'.
    
    Returns:
        float: the mean BSI, PBSI, or CPBSI value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate backscatter values for each polarization
    vh = image.select('VH')
    vv = image.select('VV')
    ratio = vv.divide(vh).rename('ratio')

    # Calculate BSI
    if type == '':
        bsi = vh.subtract(vv).divide(vh.add(vv)).rename('BSI')
    # Calculate PBSI
    elif type == 'P':
        bsi = ratio.subtract(1).divide(ratio.add(1)).rename('PBSI')
    # Calculate CPBSI
    elif type == 'CP':
        bsi = vh.subtract(ratio).divide(vh.add(ratio)).rename('CPBSI')

    # Updates the mask of the calculated BSI, PBSI, or CPBSI values to exclude any pixels where the backscatter coefficient
    # in the VV polarization is less than or equal to -20 dB (done to remove any potential noise or low-quality data points 
    # that could affect the accuracy of the index calculation) 
    bsi = bsi.updateMask(image.select('VV').gt(-20))

    # Calculate the mean xBSI for the field polygon
    return bsi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[type + 'BSI']


def calculate_tirs(image, date, polygon):
    """
    Calculate the Index of Variation of Roughness (TIRS) for a specific date and polygon in a
    Sentinel-1 image collection.

    TIRS (Index of Variation of Roughness) is an index that measures the variability of surface roughness
    in a given area, based on the difference between the backscatter signal of two perpendicular polarizations.
    It is an index that measures the change in soil roughness over time. After fertilization, the soil can become 
    more uniform, affecting the TIRS.

    Args:
        image (ee.ImageCollection): The Sentinel-1 image collection filtered by date and bounds.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.

    Returns:
        float: the mean TIRS value for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate backscatter values for each polarization
    vh = image.select('VH')
    vv = image.select('VV')

    # Calculate TIRS
    tirs = vh.subtract(vv).abs().divide(vh.add(vv)).rename('TIRS')

    # Updates the mask of the calculated TIRS values to exclude any pixels where the backscatter coefficient
    # in the VV polarization is less than or equal to -20 dB (done to remove any potential noise or low-quality data points 
    # that could affect the accuracy of the index calculation) 
    tirs = tirs.updateMask(image.select('VV').gt(-20))

    # Calculate the mean TIRS for the field polygon
    return tirs.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['TIRS']