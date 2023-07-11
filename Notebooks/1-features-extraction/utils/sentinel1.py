import ee, pandas as pd


def get_all_polarizations(image, date, polygon):
    '''
    Calculate all the mean polarization values for a specific date and polygon in a Sentinel-1 image collection.

    Sentinel-1 is a satellite mission from the European Space Agency (ESA) that carries a Synthetic Aperture Radar (SAR) instrument. 
    The SAR system is capable of transmitting and receiving radar signals in different polarizations, which refers to the orientation 
    of the electromagnetic waves as they travel through space.

    The Sentinel-1 SAR instrument can transmit and receive signals in two different polarization modes:
    - VV (vertical transmit, vertical receive): useful for detecting the roughness of surfaces, such as ocean waves or ice, as the radar 
      signal is more strongly scattered in the vertical direction.
    - VH (vertical transmit, horizontal receive): particularly useful for identifying targets with vertical structures, such as trees 
      and buildings, as it produces strong backscatter signals.

    Args:
        image (ee.ImageCollection): The Sentinel-1 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        polarizations_means (dictionary): a dictionary containing for each polarization the mean value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate the mean value over the area for the specified polarization type
    polarizations_list = ['VV', 'VH']
    polarizations_means = {}
    for polarization in polarizations_list:
        polarizations_means[polarization] = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[polarization]
    return polarizations_means


def calculate_radar_vegetation_index(polarizations_means):
    '''
    Calculate the Radar Vegetation Index (RVI) for a specific date and polygon in a Sentinel-1 image collection.
    
    Subhadip Dey: 'Vegetation indices are extremely helpful in understanding the agricultural crop conditions and
    their mapping. In optical remote sensing, Normalized Difference Vegetation Index (NDVI) is one
    such index which conveys such crop health condition within a scene. However, the limitation of
    optical remote sensing is the inability to penetrate cloud cover due to which ground data
    acquisition becomes limited within a crop growth season. Hence, a temporal gap in the acquired
    data might affect crop monitoring as well as crop mapping. On the contrary, Synthetic Aperture
    Radar (SAR) can penetrate the cloud cover, which provides the advantage of acquiring ground data
    during cloudy climatic conditions. Hence, the use of SAR data might be an appealing alternative to
    monitor crop conditions, especially during the monsoon season.'
    Formula source: https://github.com/sentinel-hub/custom-scripts/blob/master/sentinel-1/radar_vegetation_index_code_dual_polarimetric/script.js
    
    Args:
        polarizations_means (dictionary): a dictionary containing for each polarization the mean value, for a specified date and polygon.
    
    Returns:
        float: the mean RVI value, for the specified date and polygon.
    '''
    # Returns RVI
    return (polarizations_means['VH'] * 4.0) / (polarizations_means['VV'] + polarizations_means['VH'])


def calculate_simple_index(polarizations_means, type=''):
    '''
    Calculate a simple index (using VH and VV) for a specific date and polygon in a Sentinel-1 image collection.

    The functions are used to perform arithmetic operations on two bands of the data, specifically the VH and VV bands, 
    which represent the vertical and horizontal polarizations of the radar signal, respectively.
    The functions provide four options for processing the data, depending on the 'type' parameter provided:
    - AVE: This function computes the average of the VH and VV bands, which can be useful for certain applications 
      such as identifying water bodies, where the radar signal is affected by the surface roughness of the water.
    - DIF: This function computes the difference between the VH and VV bands, which can be useful for identifying 
      areas with different types of surfaces, such as vegetation and soil.
    - RAT1: This function computes the ratio of the VV and VH bands, which can be useful for identifying areas 
      with different levels of moisture content, such as wetlands or areas affected by rainfall.
    - RAT2: This function computes the ratio of the VH and VV bands, which can be useful for identifying areas 
      with different levels of roughness, such as urban areas or forests.

    Overall, these functions provide a flexible and powerful set of tools for processing Sentinel-1 radar data, 
    allowing researchers to extract valuable information about the Earth's surface and monitor changes over time.

    Formulae source: https://www.researchgate.net/publication/340548633_Combining_Radar_and_Optical_Imagery_to_Map_Oil_Palm_Plantations_in_Sumatra_Indonesia_Using_the_Google_Earth_Engine

    Args:
        polarizations_means (dictionary): a dictionary containing for each polarization the mean value, for a specified date and polygon.
        type (str): The type of simple operation to get ('AVE', 'DIF', 'RAT1', 'RAT2').

    Returns:
        float: the mean operation value for the specified date and polygon (using VH and VV polarizations).
    '''
    # Return the SIMPLE OPERATION
    if (type == 'AVE'):
        return (polarizations_means['VV'] + polarizations_means['VH']) / 2
    elif (type == 'DIF'):
        return (polarizations_means['VV'] - polarizations_means['VH'])
    elif (type == 'RAT1'):
        return (polarizations_means['VV'] / polarizations_means['VH'])
    elif (type == 'RAT2'):
        return (polarizations_means['VH'] / polarizations_means['VV'])


def calculate_normalized_difference_index(polarizations_means):
    '''
    Calculate the Normalized Difference Index (using VH and VV) for a specific date and polygon in a Sentinel-1 image collection.

    The Normalized Difference Index (NDI) is a commonly used remote sensing index that measures the difference between two spectral bands, 
    which can be helpful in Earth Observation contexts. In the case of Sentinel-1, the NDI can be computed using the VV and VH polarizations, 
    which are sensitive to different types of surfaces and features on the Earth's surface.
    The NDI is important because it can provide valuable information about various features on the Earth's surface, including vegetation, 
    water bodies, and soil moisture. For example, in the case of vegetation, the NDI can be used to estimate the biomass and vegetation health,
    as well as to detect changes in vegetation cover over time. In the case of water bodies, the NDI can be used to estimate the water content 
    and to monitor changes in water levels, which can be useful for flood forecasting and water resource management.
    In the case of soil moisture, the NDI can be used to estimate the soil moisture content, which is important for agriculture and 
    hydrology applications.
    Formula source: https://www.researchgate.net/publication/340548633_Combining_Radar_and_Optical_Imagery_to_Map_Oil_Palm_Plantations_in_Sumatra_Indonesia_Using_the_Google_Earth_Engine

    Args:
        polarizations_means (dictionary): a dictionary containing for each polarization the mean value, for a specified date and polygon.

    Returns:
        float: the mean NDI value for the specified date and polygon.
    '''
    # Calculate NDI
    return (polarizations_means['VV'] - polarizations_means['VH']) / (polarizations_means['VV'] + polarizations_means['VH'])