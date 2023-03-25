import ee, pandas as pd


def get_band(image, date, polygon, id):
    """
    Calculate the Band x value for a specific date and polygon in a Sentinel-2 image collection
    
    Spectral bands refer to specific ranges of electromagnetic radiation (EMR) that are used in remote sensing 
    applications to capture information about the earth's surface. Spectral bands are usually defined by their
    wavelength or frequency, and are typically categorized into broad groups based on their spectral characteristics, 
    such as visible, near-infrared, shortwave infrared, and thermal infrared.
    Each spectral band provides unique information about the reflectance and absorption properties of features on the
    earth's surface. For example, visible bands are sensitive to the reflectance of green vegetation, water, and soil,
    while near-infrared bands are sensitive to the reflectance of healthy vegetation. Shortwave infrared bands can detect
    differences in moisture content and mineralogy, while thermal infrared bands can detect heat signatures.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the BAND to be returned.
    
    Returns:
        float: the mean Band x value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())
    
    # Returns the mean band x value
    return image.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['B' + str(id)]


def calculate_ndvi(image, date, polygon, type="", id=None):
    """
    Calculates the xNDVI index for a given image, date, and polygon.
    
    While all of the listed NDVI indices are used to assess vegetation health and density, they differ in 
    the specific wavelengths of light that are used to calculate the index:
    - NDVI (Normalized Difference Vegetation Index) uses the difference between visible red and near-infrared wavelengths of light.
    - NSNDVI (NIR-SWIR NDVI) uses the difference between near-infrared and shortwave infrared wavelengths of light.
    - GNDVI (Green NDVI) uses the difference between green and near-infrared wavelengths of light.
    - RENDVI (Red Edge NDVI) uses the difference between red edge and near-infrared wavelengths of light.
    - GRNDVI (Green-Red NDVI) uses the difference between green and red wavelengths of light.
    - GBNDVI (Green-Blue NDVI) uses the difference between green and blue wavelengths of light.

    Each of these indices may have different strengths and weaknesses depending on the specific vegetation types
    and environmental conditions being studied. For example, some indices may be more sensitive to vegetation 
    stress or changes in leaf structure than others. Therefore, researchers and practitioners may choose 
    different NDVI indices depending on their specific research questions and the available data.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        type (str): The type of normalized difference vegetation index to calculate (default is 'NDVI'). 
            Other options include 'NS', 'G', 'RE', 'GR and 'GB'.
        id (int): The id of the specified type of normalized difference vegetation index to calculate (it 
            is used just for the RENDVI actually)
            
    Returns:
        float: the calculated xNDVI value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate NDVI
    if (type == ""):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    elif (type == "NS"):
        ndvi = image.normalizedDifference(['B11', 'B7']).rename('NSNDVI')
    elif (type == "G"):
        ndvi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    elif (type == "RE"):
        if (id == 1):
            ndvi = image.normalizedDifference(['B5', 'B4']).rename('RENDVI1')
        elif (id == 2):
            ndvi = image.normalizedDifference(['B6', 'B4']).rename('RENDVI2')
        elif (id == 3):
            ndvi = image.normalizedDifference(['B7', 'B4']).rename('RENDVI3')
    elif (type == "GR"):
        b3 = image.select('B3')
        b4 = image.select('B4')
        b8 = image.select('B8')
        ndvi = ((b8.subtract(b3.add(b4)))).divide(b8.add(b3.add(b4))).rename('GRNDVI')
    elif (type == "GB"):
        b2 = image.select('B2')
        b3 = image.select('B3')
        b8 = image.select('B8')
        ndvi = ((b8.subtract(b3.add(b2)))).divide(b8.add(b3.add(b2))).rename('GBNDVI')

    # Mask out clouds and shadows
    ndvi = ndvi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean xNDVI for the field polygon
    return ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[type + 'NDVI' + '' if id == None else str(id)]


def calculate_eomi(image, date, polygon, id):
    """
    Calculates the EOMIx (Exogenous Organic Matter Index) index for a given image, date, and polygon.

    The Exogenous Organic Matter Index (EOMI) is a soil quality indicator used to assess the content and quality of
    organic matter in soil. The EOMI is sensitive to the quantity and quality of exogenous organic matter, such as 
    crop residues, manure, and other organic inputs, as well as the presence of mineral and inorganic components in soil.
    For further details read the following paper: https://www.mdpi.com/2072-4292/13/9/1616.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the EOMI to be calculated (from 1 to 4).
        
    Returns:
        float: the calculated EOMIx value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate EOMI (different with respect to the passed id)
    if (id == 1):
        eomi = image.normalizedDifference(['B11', 'B8A']).rename('EOMI1')
    if (id == 2):
        eomi = image.normalizedDifference(['B12', 'B4']).rename('EOMI2')
    if (id == 3):
        b11 = image.select('B11')
        b8a = image.select('B8A')
        b12 = image.select('B12')
        b04 = image.select('B4')
        eomi = ((b11.subtract(b8a)).add(b12.add(b04))).divide(b11.add(b8a).add(b12).add(b04)).rename('EOMI3')
    if (id == 4):
        eomi = image.normalizedDifference(['B11', 'B4']).rename('EOMI4')

    # Mask out clouds and shadows
    eomi = eomi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean EOMI for the field polygon
    return eomi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['EOMI' + str(id)]


def calculate_savi(image, date, polygon, type=""):
    """
    Calculate the xSAVI index for a specific date and polygon in a Sentinel-2 image collection
    
    This function calculates a specified vegetation index, such as SAVI, MSAVI, OSAVI, or TSAVI, for a specific date and 
    polygon in a Sentinel-2 image collection.
    - SAVI (Soil Adjusted Vegetation Index) was developed to minimize the influence of soil brightness on vegetation indices. 
      SAVI uses a soil adjustment factor to reduce the noise caused by soil brightness. It is particularly useful in areas 
      with sparse vegetation.
    - OSAVI (Optimized SAVI) is similar to SAVI, but it has been optimized to better handle areas
      with dense vegetation. OSAVI was developed to reduce the saturation effect seen in SAVI at high vegetation densities.
    - MSAVI (Modified SAVI) is a modification of SAVI that is designed to reduce the noise and saturation
      issues in areas with dense vegetation. MSAVI is often used in agricultural applications.
    - TSAVI (Transformed SAVI) is a variation of SAVI that uses a different soil adjustment factor to
      reduce the influence of soil brightness on vegetation indices. TSAVI is particularly useful in arid and semi-arid regions.
    - ATSAVI (Adjusted Transformed SAVI) an extension of TSAVI that further accounts for atmospheric interference. It uses an additional
      atmospheric correction factor to account for the influence of aerosols and atmospheric conditions on vegetation indices.
      This makes it more effective than TSAVI in areas with high aerosol content or other atmospheric disturbances, such as urban 
      areas or areas affected by wildfires.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        type (str): The type of vegetation index to calculate (default is 'SAVI'). Other options include 'M', 
                    'O', 'T' and 'AT'.
    
    Returns:
        float: the mean value of the specified xSAVI, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    nir = image.select('B8')
    red = image.select('B4')

    # Calculate the specified vegetation index
    if (type == ''):
        L = 0.428
        savi = (nir.subtract(red)).divide(nir.add(red).add(L)).multiply(1 + L).rename('SAVI')
    elif (type == 'M'):
        savi = nir.multiply(2.0).add(1.0).subtract(nir.multiply(2.0).add(1.0).pow(2).subtract(nir.subtract(red).multiply(8.0)).sqrt()).divide(2.0).rename('MSAVI')
    elif (type == 'O'):
        savi = nir.subtract(red).multiply(1.0 + 0.16).divide(nir.add(red).add(0.16)).rename('OSAVI')
    elif (type == 'T'):
        X, A, B = 0.114, 0.824, 0.421
        savi = nir.subtract(B.multiply(red).subtract(A)).multiply(B).divide(red.add(B.multiply(nir.subtract(A))).add(X.multiply(1.0 + B.pow(2.0)))).rename('TSAVI')
    elif (type == 'AT'):
        savi = nir.subtract(1.22.multiply(red).subtract(0.03)).divide(nir.add(red).subtract(1.22.multiply(0.03)).add(0.08.multiply(1.0.add(1.22.pow(2.0))))).rename('ATSAVI')

    # Mask out clouds and shadows
    savi = savi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean vegetation index for the field polygon
    return savi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[type + 'SAVI']


def calculate_nbr(image, date, polygon, id=None):
    """
    Calculate the Normalized Burn Ratio (NBR) value for a specific date and polygon in a Sentinel-2 image collection
    
    The Normalized Burn Ratio is a remote sensing index used to detect and quantify the severity of burn scars
    caused by wildfires. 
    NBR2 is an enhancement of the original Normalized Burn Ratio (NBR) index, which was developed for the same purpose.
    The NBR2 index is sensitive to changes in the vegetation and the charred biomass resulting from a fire, as well as the 
    presence of unburned vegetation and soil background. 
    The values of NBR2 range from -1 to 1, with higher values indicating more severe burn scars. The index is particularly 
    useful in detecting the extent and severity of burn scars in heavily vegetated areas.
    The NBR2 is commonly used in wildfire monitoring and management, as well as in post-fire ecological and land use assessments.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the NBR to be calculated (default is the standard version).
    
    Returns:
        float: the mean NBR2 value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate NBR
    if (id == None):
        nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR')
    elif (id == 2):
        nbr = image.normalizedDifference(['B11', 'B12']).rename('NBR2')

    # Mask out clouds and shadows
    nbr = nbr.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean NDVI for the field polygon
    return nbr.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['NBR' + str(id) if id != None else '']


def calculate_chlorophyll_index(image, date, polygon, id):
    """
    Calculates the Chlorophyll Index (CI) for a given image, date, and polygon.

    The Chlorophyll Index (CI) is a vegetation index used to estimate chlorophyll content in vegetation. It is calculated
    using the ratio of the near-infrared (NIR) and red (RED) bands of Sentinel-2.
    In general, CI1 is more commonly used and provides a good estimate of chlorophyll content in a variety of vegetation types. 
    However, CI2 may be more suitable for some applications, such as in areas with dense vegetation or where structural properties
    of vegetation are important to consider.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the CI index to be calculated (from 1 to 3).

    Returns:
        float: the calculated CI value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate CI (different with respect to the passed id)
    if (id == 1):
        ci = image.select('B8').divide(image.select('B5')).subtract(1).rename('CI1')
    elif (id == 2):
        ci = image.select('B8').divide(image.select('B6')).subtract(1).rename('CI2')
    elif (id == 3):
        ci = image.select('B8').divide(image.select('B7')).subtract(1).rename('CI3')

    # Mask out clouds and shadows
    ci = ci.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean CI for the field polygon
    return ci.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['CI' + str(id)]


def compute_green_coverage_index(image, date, polygon):
    """
    Calculate the Green Coverage Index (GCI) for a specific date and polygon in a Sentinel-2 image collection
    
    GCI is a vegetation index that is designed to be less sensitive to atmospheric and soil background effects. It can 
    be used to estimate the fractional green vegetation cover in a given area.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the GCI, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b3 = image.select('B3')
    b9 = image.select('B9')

    # Calculate the GCI
    gci = b9.divide(b3).subtract(1).rename('GCI')

    # Mask out clouds and shadows
    gci = gci.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean vegetation index for the field polygon
    return gci.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['GCI']


def compute_soil_composition_index(image, polygon, date):
    """
    Computes the Soil Composition Index (SCI) for a specified date and polygon in a Sentinel-2 image collection.
    
    The Soil Composition Index (SCI) is a measure of soil composition that is useful for identifying areas with high 
    mineral content, such as desert environments. It is calculated as (B11 - B08) / (B11 + B08).
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
    
    Returns:
        float: The mean value of the Soil Composition Index (SCI) for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b11 = image.select('B11')
    b8 = image.select('B8')

    # Calculate the Soil Composition Index (SCI)
    sci = b11.subtract(b8).divide(b11.add(b8)).rename('SCI')

    # Mask out clouds and shadows
    sci = sci.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean SCI for the field polygon
    return sci.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['SCI']


def calculate_ndre(image, polygon, date, id):
    """
    Calculates the Normalized Difference Red Edge (NDRE) index for a given image, date, and polygon.

    The Normalized Difference Red Edge (NDRE) is a vegetation index used to assess plant chlorophyll and nitrogen
    content. NDRE is sensitive to the presence of healthy, green vegetation and is useful for monitoring crop health,
    stress, and growth.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        id (int): The id of the NDRE to be calculated (from 1 to 3).

    Returns:
        float: the calculated NDREx value, for the specified date and polygon.
    """
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate NDRE
    if (id == 1):
        ndre = image.normalizedDifference(['B08', 'B05']).rename('NDRE1')
    elif (id == 2):
        ndre = image.normalizedDifference(['B08', 'B06']).rename('NDRE2')
    elif (id == 3):
        ndre = image.normalizedDifference(['B08', 'B07']).rename('NDRE3')

    # Mask out clouds and shadows
    ndre = ndre.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean NDRE for the field polygon
    return ndre.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['NDRE' + str(id)]