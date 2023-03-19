
import ee, pandas as pd

def calculate_ndvi(image, date, polygon):
    """
    Calculates the NDVI index for a given image, date, and polygon.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        
    Returns:
        The calculated NDVI value for the specified date and polygon.
    """
    # Convert date to Earth Engine format
    date_ee = ee.Date(date.strftime("%Y-%m-%d"))

    # Select the image for the specified date
    image = image.filterDate(date_ee, date_ee.advance(1, 'day')).first()

    # Calculate NDVI
    ndvi = image.normalizedDifference('B8', 'B4')

    # Mask out clouds and shadows
    ndvi = ndvi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean NDVI for the field polygon
    ndvi_mean = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('nd')

    return ndvi_mean.getInfo()


def calculate_eomi(image, date, polygon):
    """
    Calculates the EOMI index for a given image, date, and polygon.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        
    Returns:
        The calculated EOMI value for the specified date and polygon.
    """
    # Convert date to Earth Engine format
    date_ee = ee.Date(date.strftime("%Y-%m-%d"))

    # Select the image for the specified date
    image = image.filterDate(date_ee, date_ee.advance(1, 'day')).first()

    # Calculate EOMI
    eomi = image.expression('(B8-B4)/(B8+B4)')

    # Mask out clouds and shadows
    eomi = eomi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean EOMI for the field polygon
    eomi_mean = eomi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('constant')

    return eomi_mean.getInfo()


def calculate_b1(image, date, polygon):
    """
    Calculate the band 1 value for a specific date and polygon in a Sentinel-2 image collection
    
    Args:
        image: ee.ImageCollection, Sentinel-2 image collection
        date: pd.Timestamp, date to calculate band 1 for
        polygon: ee.Geometry.Polygon, field boundary polygon
    
    Returns:
        Float, band 1 value
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Clip image to polygon boundary
    clipped_image = image.clip(polygon)
    
    # Calculate band 1 value
    band1 = clipped_image.select('B1').reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('B1')
    
    return band1.getInfo()


def calculate_b3(image, date, polygon):
    """
    Calculate the band 3 value for a specific date and polygon in a Sentinel-2 image collection
    
    Args:
        image: ee.ImageCollection, Sentinel-2 image collection
        date: pd.Timestamp, date to calculate band 3 for
        polygon: ee.Geometry.Polygon, field boundary polygon
    
    Returns:
        Float, band 3 value
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Clip image to polygon boundary
    clipped_image = image.clip(polygon)
    
    # Calculate band 3 value
    band3 = clipped_image.select('B3').reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('B3')
    
    return band3.getInfo()


def calculate_vh(image, date, polygon):
    """
    Calculate the mean VH polarization value for a specific date and polygon in a Sentinel-1 image collection
    
    Args:
        image: ee.ImageCollection, Sentinel-1 image collection
        date: pd.Timestamp, date to calculate VH polarization for
        polygon: ee.Geometry.Polygon, field boundary polygon
    
    Returns:
        Float, VH polarization value
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Clip image to polygon boundary
    clipped_image = image.clip(polygon)
    
    # Calculate VH polarization value
    vh = clipped_image.select('VH').reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('VH')
    
    return vh.getInfo()


def calculate_vv(image, date, polygon):
    """
    Calculates the mean of the VV polarization values for an image at a given date and polygon.

    Parameters:
        image (ee.ImageCollection): An ImageCollection to calculate the index from.
        date (str or pd.Timestamp): The date to calculate the index for, in format 'yyyy-mm-dd'.
        polygon (ee.Geometry): An ee.Geometry polygon representing the field of interest.

    Returns:
        float: The mean of the VV polarization values
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Clip image to polygon boundary
    clipped_image = image.clip(polygon)
    
    # Calculate VH polarization value
    vv = clipped_image.select('VV').reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon, scale=10).get('VV')
    
    return vv.getInfo()