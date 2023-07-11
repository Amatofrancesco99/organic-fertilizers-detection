import ee, pandas as pd
from math import sqrt


def get_all_bands(image, date, polygon):
    '''
    Calculate all the Sentinel-2 bands mean values for a specific date and polygon in a Sentinel-2 image collection.
    
    Spectral bands refer to specific ranges of electromagnetic radiation (EMR) that are used in remote sensing 
    applications to capture information about the earth's surface. Spectral bands are usually defined by their
    wavelength or frequency, and are typically categorized into broad groups based on their spectral characteristics, 
    such as visible, near-infrared, and shortwave infrared.
    Each spectral band provides unique information about the reflectance and absorption properties of features on the
    earth's surface. For example, visible bands are sensitive to the reflectance of green vegetation, water, and soil,
    while near-infrared bands are sensitive to the reflectance of healthy vegetation. Finally, shortwave infrared bands
    can detect differences in moisture content and mineralogy.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Mask out clouds and shadows
    image = image.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))
    
    # Returns the list of mean bands values
    bands_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']
    bands_means = {}
    for band in bands_list:
        bands_means[band] = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[band]
    return bands_means


def calculate_vegetation_index(bands_means, type, id=None):
    '''
    Calculates the specified VI index for a given image, date, and polygon.
    
    While all of the listed VI indices are used to assess vegetation health and density, they differ in 
    the specific wavelengths of light that are used to calculate the index.

    Each of these indices may have different strengths and weaknesses depending on the specific vegetation types
    and environmental conditions being studied. For example, some indices may be more sensitive to vegetation 
    stress or changes in leaf structure than others. Therefore, researchers and practitioners may choose 
    different VI indices depending on their specific research questions and the available data.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        type (str): The type of vegetation index to calculate.
        id (int): The id of the specified type of vegetation index to calculate.
            
    Returns:
        float: the calculated VI value, for the specified date and polygon.
    '''
    # Return NDVI
    if (type == 'ND'):
        return (bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + bands_means['B4'])
    elif (type == 'NSND'):
        return (bands_means['B11'] - bands_means['B7']) / (bands_means['B11'] + bands_means['B7'])
    elif (type == 'GND'):
        return (bands_means['B8'] - bands_means['B3']) / (bands_means['B8'] + bands_means['B3'])
    elif (type == 'REND'):
        if (id == 1):
            return (bands_means['B5'] - bands_means['B4']) / (bands_means['B5'] + bands_means['B4'])
        elif (id == 2):
            return (bands_means['B6'] - bands_means['B4']) / (bands_means['B6'] + bands_means['B4'])
        elif (id == 3):
            return (bands_means['B7'] - bands_means['B4']) / (bands_means['B7'] + bands_means['B4'])
    elif (type == 'GRND'):
        return (bands_means['B8'] - (bands_means['B3'] + bands_means['B4'])) / (bands_means['B8'] + (bands_means['B3'] + bands_means['B4']))
    elif (type == 'GBND'):
        return (bands_means['B8'] - (bands_means['B3'] + bands_means['B2'])) / (bands_means['B8'] + (bands_means['B3'] + bands_means['B2']))


    # Return SAVI
    elif (type == 'SA'):
        L = 0.428
        return (bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + bands_means['B4'] + L) * (1 + L)
    elif (type == 'MSA'):
        return (2.0 * bands_means['B8'] + 1.0 - sqrt(((2.0 * bands_means['B8'] + 1.0) ** 2.0) - 8.0 * (bands_means['B8'] - bands_means['B4']))) / 2.0
    elif (type == 'OSA'):
        return (1.0 + 0.16) * (bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + bands_means['B4'] + 0.16)
    elif (type == 'TSA'):
        X, A, B = 0.114, 0.824, 0.421
        return (B * (bands_means['B8'] - B * bands_means['B4'] - A)) / (bands_means['B4'] + B * (bands_means['B8'] - A) + X * (1.0 + (B ** 2.0)))
    elif (type == 'ATSA'):
        return 1.22 * (bands_means['B8'] - 1.22 * bands_means['B4'] - 0.03) / (1.22 * bands_means['B8'] + bands_means['B4'] - 1.22 * 0.03 + 0.08 * (1.0 + (1.22 ** 2.0)))


    # Other VIs
    elif (type == 'A'):
        return (bands_means['B8'] * (1 - bands_means['B4'])*(bands_means['B8'] - bands_means['B4'])) ** 1/3
    elif (type == 'AR'):
        if (id == 1):
            return (bands_means['B8A'] - bands_means['B4'] - 0.069 * (bands_means['B4'] - bands_means['B2'])) / (bands_means['B8A'] + bands_means['B4'] - 0.069 * (bands_means['B4'] - bands_means['B2']))
        elif (id == 2):
            return -0.18 + 1.17 * ((bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + bands_means['B4']))
    elif (type == 'C'):
        return (bands_means['B8'] * bands_means['B4']) / (bands_means['B3'] ** 2.0)
    elif (type == 'CT'):
        return (((bands_means['B4'] - bands_means['B3']) / (bands_means['B4'] + bands_means['B3'])) + 0.5) / (abs(((bands_means['B4'] - bands_means['B3']) / (bands_means['B4'] + bands_means['B3']))) + 0.5 * sqrt(abs((((bands_means['B4'] - bands_means['B3']) / (bands_means['B4'] + bands_means['B3']))) + 0.5)))
    elif (type == 'D'):
        return bands_means['B8'] - bands_means['B4']
    elif (type == 'E'):
        if (id == 1):
            return 2.5 * (bands_means['B8'] - bands_means['B4']) / ((bands_means['B8'] + 6.0 * bands_means['B4'] - 7.5 * bands_means['B2']) + 1.0)
        elif (id == 2):
            return 2.4 * (bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + bands_means['B4'] + 1.0)
        elif (id == 3):
            return 2.5 * (bands_means['B8'] - bands_means['B4']) / (bands_means['B8'] + 2.4 * bands_means['B4'] + 1.0)
    elif (type == 'MT'):
        if (id == 1):
            return 1.2 * (1.2 * (bands_means['B8'] - bands_means['B3']) - 2.5 * (bands_means['B4'] - bands_means['B3']))
        elif (id == 2):
            return 1.5 * (1.2 * (bands_means['B8'] - bands_means['B3']) - 2.5 * (bands_means['B4'] - bands_means['B3'])) / sqrt(((2.0 * bands_means['B8'] + 1.0) ** 2.0) - (6.0 * bands_means['B8'] - 5.0 * sqrt(bands_means['B4'])) - 0.5)
    elif (type == 'R'):
        return bands_means['B8'] / bands_means['B4'] 
    elif (type == 'WDR'):
        return (0.1 * bands_means['B8'] - bands_means['B4']) / (0.1 * bands_means['B8'] + bands_means['B4'])


def calculate_exogenous_organic_matter_index(bands_means, id):
    '''
    Calculates the EOMIx (Exogenous Organic Matter Index) index for a given image, date, and polygon.

    The Exogenous Organic Matter Index (EOMI) is a soil quality indicator used to assess the content and quality of
    organic matter in soil. The EOMI is sensitive to the quantity and quality of exogenous organic matter, such as 
    crop residues, manure, and other organic inputs, as well as the presence of mineral and inorganic components in soil.
    For further details read the following paper: https://www.mdpi.com/2072-4292/13/9/1616.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the EOMI to be calculated (from 1 to 4).
        
    Returns:
        float: the calculated EOMIx value, for the specified date and polygon.
    '''
    # Calculate EOMI (different with respect to the passed id)
    if (id == 1):
        return (bands_means['B11'] - bands_means['B8A']) / (bands_means['B11'] + bands_means['B8A'])
    if (id == 2):
        return (bands_means['B12'] - bands_means['B4']) / (bands_means['B12'] + bands_means['B4'])
    if (id == 3):
        return ((bands_means['B11'] - bands_means['B8A']) + (bands_means['B12'] - bands_means['B4'])) / (bands_means['B11'] + bands_means['B8A'] + bands_means['B12'] + bands_means['B4'])
    if (id == 4):
        return (bands_means['B11'] - bands_means['B4']) / (bands_means['B11'] + bands_means['B4'])


def calculate_normalized_burn_ratio(bands_means, id=None):
    '''
    Calculate the Normalized Burn Ratio (NBR) value for a specific date and polygon in a Sentinel-2 image collection.
    
    The Normalized Burn Ratio is a remote sensing index used to detect and quantify the severity of burn scars
    caused by wildfires. 
    NBR2 is an enhancement of the original Normalized Burn Ratio (NBR) index, which was developed for the same purpose.
    The NBR2 index is sensitive to changes in the vegetation and the charred biomass resulting from a fire, as well as the 
    presence of unburned vegetation and soil background. 
    The values of NBR2 range from -1 to 1, with higher values indicating more severe burn scars. The index is particularly 
    useful in detecting the extent and severity of burn scars in heavily vegetated areas.
    The NBR2 is commonly used in wildfire monitoring and management, as well as in post-fire ecological and land use assessments.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the NBR to be calculated (default is the standard version).
    
    Returns:
        float: the mean NBRx value, for the specified date and polygon.
    '''
    # Calculate NBR
    if (id == None):
        return (bands_means['B8'] - bands_means['B12']) / (bands_means['B8'] + bands_means['B12'])
    elif (id == 2):
        return (bands_means['B11'] - bands_means['B12']) / (bands_means['B11'] + bands_means['B12'])


def calculate_chlorophyll_index(bands_means, id):
    '''
    Calculates the Chlorophyll Index (CI) for a given image, date, and polygon.

    The Chlorophyll Index (CI) is a vegetation index used to estimate chlorophyll content in vegetation. It is calculated
    using the ratio of the near-infrared (NIR) and red (RED) bands of Sentinel-2.
    In general, CI1 is more commonly used and provides a good estimate of chlorophyll content in a variety of vegetation types. 
    However, CI2 may be more suitable for some applications, such as in areas with dense vegetation or where structural properties
    of vegetation are important to consider.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the CI index to be calculated (from 1 to 3).

    Returns:
        float: the calculated CI value, for the specified date and polygon.
    '''
    # Calculate CI (different with respect to the passed id)
    if (id == 1):
        return (bands_means['B8'] / bands_means['B5']) - 1
    elif (id == 2):
        return (bands_means['B8'] / bands_means['B6']) - 1
    elif (id == 3):
        return (bands_means['B8'] / bands_means['B7']) - 1


def calculate_green_coverage_index(bands_means):
    '''
    Calculate the Green Coverage Index (GCI) for a specific date and polygon in a Sentinel-2 image collection.
    
    GCI is a vegetation index that is designed to be less sensitive to atmospheric and soil background effects. It can 
    be used to estimate the fractional green vegetation cover in a given area.
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: the mean value of the GCI, for the specified date and polygon.
    '''
    # Calculate the mean vegetation index for the field polygon
    return (bands_means['B9'] / bands_means['B3']) - 1


def calculate_soil_composition_index(bands_means):
    '''
    Calculates the Soil Composition Index (SCI) for a specified date and polygon in a Sentinel-2 image collection.
    
    The Soil Composition Index (SCI) is a measure of soil composition that is useful for identifying areas with high 
    mineral content, such as desert environments. It is calculated as (B11 - B8) / (B11 + B8).
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: The mean value of the Soil Composition Index (SCI) for the specified date and polygon.
    '''
    # Calculate the mean SCI for the field polygon
    return (bands_means['B11'] - bands_means['B8']) / (bands_means['B11'] + bands_means['B8'])


def calculate_normalized_difference_red_edge(bands_means, id):
    '''
    Calculates the Normalized Difference Red Edge (NDRE) index for a given image, date, and polygon.

    The Normalized Difference Red Edge (NDRE) is a vegetation index used to assess plant chlorophyll and nitrogen
    content. NDRE is sensitive to the presence of healthy, green vegetation and is useful for monitoring crop health,
    stress, and growth.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the NDRE to be calculated (from 1 to 3).

    Returns:
        float: the calculated NDREx value, for the specified date and polygon.
    '''
    # Calculate NDRE
    if (id == 1):
        return (bands_means['B8'] - bands_means['B5']) / (bands_means['B8'] + bands_means['B5'])
    elif (id == 2):
        return (bands_means['B8'] - bands_means['B6']) / (bands_means['B8'] + bands_means['B6'])
    elif (id == 3):
        return (bands_means['B8'] - bands_means['B7']) / (bands_means['B8'] + bands_means['B7'])


def calculate_modified_chlorophyll_absorption_reflectance_index(bands_means, id=None):
    '''
    Calculates the Modified Chlorophyll Absorption in Reflectance Index (MCARI, MCARI1, MCARI2) for a given image, date, and polygon.

    MCARI is a vegetation index used to estimate chlorophyll content in vegetation, and is based on the difference between the 
    green and red reflectances, weighted by the green reflectance. MCARI1 and MCARI2 are modified versions of MCARI, with different 
    weighting factors for the green and red reflectances.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the MCARI index to be calculated (from 0 to 2 - default None).

    Returns:
        float: the calculated MCARI value, for the specified date and polygon.
    '''
    # Calculate MCARI (different with respect to the passed id)
    if (id == None):
        return ((bands_means['B5'] - bands_means['B4']) - 0.2 * (bands_means['B5'] - bands_means['B3'])) * (bands_means['B5'] / bands_means['B4'])
    elif (id == 1):
        return  1.2 * (2.5 * (bands_means['B8'] - bands_means['B4']) - 1.3 * (bands_means['B8'] - bands_means['B3']))
    elif (id == 2):
        return 1.5 * (2.5 * (bands_means['B8'] - bands_means['B4']) - 1.3 * (bands_means['B8'] - bands_means['B3'])) / sqrt(((2.0 * bands_means['B8'] + 1.0) ** 2.0) - (6.0 * bands_means['B8'] - 5.0 * sqrt(bands_means['B4'])) - 0.5)
   

def calculate_chlorophyll_absorption_ratio_index(bands_means, id):
    '''
    Calculates the Chlorophyll Absorption Ratio Index (CARI) for a given image, date, and polygon.

    The Chlorophyll Absorption Ratio Index (CARI) is a vegetation index used to estimate the amount of chlorophyll
    content in vegetation. It is calculated using the ratio of the near-infrared (NIR) and red (RED) bands of Sentinel-2,
    as well as the blue (BLUE) and green (GREEN) bands.

    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
        id (int): The id of the CARI index to be calculated (from 1 to 2).

    Returns:
        float: the calculated CARI value, for the specified date and polygon.
    '''
    # Calculate CARI
    if (id == 1):
        return (bands_means['B5'] / bands_means['B4']) * (sqrt((((bands_means['B5'] - bands_means['B3']) / 150.0 * 670.0 + bands_means['B4'] + (bands_means['B3'] - ((bands_means['B5'] - bands_means['B3']) / 150.0 * 550.0))) ** 2.0))) / (((((bands_means['B5'] - bands_means['B3']) / (150.0 ** 2.0) + 1.0) ** 0.5)))
    elif (id == 2):
        return (abs((((bands_means['B5'] - bands_means['B3']) / 150.0) * bands_means['B4'] + bands_means['B4'] + bands_means['B3'] - (0.496 * bands_means['B3']))) / ((((0.496 ** 2.0) + 1.0) ** 0.5) * (bands_means['B5'] / bands_means['B4'])))


def calculate_bare_soil_index(bands_means):
    '''
    Calculate the Bare Soil Index (BSI) for a specific date and polygon in a Sentinel-2 image collection.
    
    BSI is a vegetation index that can be used to estimate the percentage of bare soil in a given area.
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: the mean value of the BSI, for the specified date and polygon.
    '''
    # Calculate the mean BSI for the field polygon
    return (bands_means['B11'] + bands_means['B4']) + ((bands_means['B8'] + bands_means['B2']) / (bands_means['B11'] + bands_means['B4'])) + (bands_means['B8'] + bands_means['B2'])


def calculate_green_leaf_index(bands_means):
    '''
    Calculate the Green Leaf Index (GLI) for a specific date and polygon in a Sentinel-2 image collection.
    
    GLI is a vegetation index that is designed to be less sensitive to atmospheric and soil background effects. It can 
    be used to estimate the fractional green vegetation cover in a given area.
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: the mean value of the GLI, for the specified date and polygon.
    '''
    # Calculate the mean vegetation index for the field polygon
    return (2.0 * bands_means['B3'] - bands_means['B4'] - bands_means['B2']) / (2.0 * bands_means['B3'] + bands_means['B4'] + bands_means['B2'])


def calculate_alteration_index(bands_means):
    '''
    Calculate the Alteration index for a specific date and polygon in a Sentinel-2 image collection.
    
    Alteration index is used to map the presence of Al-OH or Fe-OH minerals in rocks, and is particularly useful in 
    mapping alteration zones around ore deposits.
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: the mean value of the Alteration index, for the specified date and polygon.
    '''
    # Calculate the mean Alteration index for the field polygon
    return bands_means['B11'] / bands_means['B12']


def calculate_swir_difference_index(bands_means):
    '''
    Calculate the SWIR Difference Index (SDI) for a specific date and polygon in a Sentinel-2 image collection.
    
    SDI is a band ratio index that highlights moisture content and can be used to monitor changes in vegetation
    moisture content, soil moisture, and mineralogical composition.
    
    Args:
        bands_means (dictionary): a dictionary containing for each band the mean value, for the specified date and polygon.
    
    Returns:
        float: the mean value of the SDI, for the specified date and polygon.
    '''
    # Calculate the mean SDI for the field polygon
    return bands_means['B8'] - bands_means['B12']