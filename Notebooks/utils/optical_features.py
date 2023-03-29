import ee, pandas as pd


def get_band(image, date, polygon, id):
    '''
    Calculate the Band X value for a specific date and polygon in a Sentinel-2 image collection.
    
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
        float: the mean Band X value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())
    
    # Returns the mean band x value
    return image.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['B' + str(id)]


def calculate_vegetation_index(image, date, polygon, type, id=None):
    '''
    Calculates the specified VI index for a given image, date, and polygon.
    
    While all of the listed VI indices are used to assess vegetation health and density, they differ in 
    the specific wavelengths of light that are used to calculate the index.

    Each of these indices may have different strengths and weaknesses depending on the specific vegetation types
    and environmental conditions being studied. For example, some indices may be more sensitive to vegetation 
    stress or changes in leaf structure than others. Therefore, researchers and practitioners may choose 
    different VI indices depending on their specific research questions and the available data.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        type (str): The type of vegetation index to calculate.
        id (int): The id of the specified type of vegetation index to calculate.
            
    Returns:
        float: the calculated VI value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    nir = image.select('B8')
    red = image.select('B4')

    # Calculate NDVI
    if (type == 'ND'):
        vi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    elif (type == 'NSND'):
        vi = image.normalizedDifference(['B11', 'B7']).rename('NSNDVI')
    elif (type == 'GND'):
        vi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI')
    elif (type == 'REND'):
        if (id == 1):
            vi = image.normalizedDifference(['B5', 'B4']).rename('RENDVI1')
        elif (id == 2):
            vi = image.normalizedDifference(['B6', 'B4']).rename('RENDVI2')
        elif (id == 3):
            vi = image.normalizedDifference(['B7', 'B4']).rename('RENDVI3')
    elif (type == 'GRND'):
        b3 = image.select('B3')
        vi = ((nir.subtract(b3.add(red)))).divide(nir.add(b3.add(red))).rename('GRNDVI')
    elif (type == 'GBND'):
        b2 = image.select('B2')
        b3 = image.select('B3')
        vi = ((nir.subtract(b3.add(b2)))).divide(nir.add(b3.add(b2))).rename('GBNDVI')

    # Calculate SAVI
    elif (type == 'SA'):
        L = 0.428
        vi = (nir.subtract(red)).divide((nir.add(red).add(L)).multiply(1 + L)).rename('SAVI')
    elif (type == 'MSA'):
        vi = nir.multiply(2.0).add(1.0).subtract(nir.multiply(2.0).add(1.0).pow(2).subtract(nir.subtract(red).multiply(8.0)).sqrt()).divide(2.0).rename('MSAVI')
    elif (type == 'OSA'):
        vi = (nir.subtract(red).multiply(1.0 + 0.16)).divide(nir.add(red).add(0.16)).rename('OSAVI')
    elif (type == 'TSA'):
        X, A, B = 0.114, 0.824, 0.421
        vi = nir.subtract(ee.Image.constant(B).multiply(red).subtract(A)).multiply(B).divide(red.add(ee.Image.constant(B).multiply(nir.subtract(A))).add(ee.Image.constant(X).multiply(1 + B ** 2.0))).rename('TSAVI')
    elif (type == 'ATSA'):
        vi = nir.subtract(ee.Image.constant(1.22).multiply(red).subtract(0.03)).divide(nir.add(red).subtract(ee.Image.constant(1.22).multiply(0.03)).add(ee.Image.constant(0.08).multiply(1.0 + 1.22 ** 2.0))).rename('ATSAVI')

    # Other VIs
    elif (type == 'A'):
        vi = (nir.multiply((ee.Image.constant(1.0).subtract(red))).multiply(nir.subtract(red))).pow(1.0/3.0).rename('AVI')
    elif (type == 'AR'):
        b2 = image.select('B2')
        b8a = image.select('B8A')
        if (id == 1):
            vi = (b8a.subtract(red).subtract(0.069).multiply(red.subtract(b2))).divide(b8a.add(red).subtract(0.069).multiply(red.subtract(b2))).rename('ARVI1')
        elif (id == 2):
            vi = ee.Image.constant(-0.18).add(ee.Image.constant(1.17).multiply(nir.subtract(red).divide(nir.add(red)))).rename('ARVI2')
    elif (type == 'C'):
        b3 = image.select('B3')
        vi = (nir.multiply(red)).divide(b3.pow(2.0)).rename('CVI')
    elif (type == 'CT'):
        b3 = image.select('B3')
        vi = (red.subtract(b3).divide(red.add(b3))).add(0.5).divide((red.subtract(b3).divide(red.add(b3))).add(0.5).abs()).multiply(((red.subtract(b3).divide(red.add(b3))).add(0.5)).abs().sqrt()).rename('CTVI')
    elif (type == 'D'):
        vi = nir.subtract(red).rename('DVI')
    elif (type == 'E'):
        if (id == 1):
            b2 = image.select('B2')
            vi = (nir.subtract(red).multiply(2.5)).divide((nir.add(red.multiply(6.0)).subtract(b2.multiply(7.5))).add(1.0)).rename('EVI1')
        elif (id == 2):
            vi = (nir.subtract(red).multiply(2.4)).divide(nir.add(red).add(1.0)).rename('EVI2')
        elif (id == 3):
            vi = (nir.subtract(red).multiply(2.5)).divide(nir.add(red.multiply(2.4)).add(1.0)).rename('EVI3')
    elif (type == 'MT'):
        b3 = image.select('B3')
        if (id == 1):
            vi = (nir.subtract(b3).multiply(1.2).subtract(red.subtract(b3).multiply(2.5))).multiply(1.2).rename('MTVI1')
        elif (id == 2):
            vi = nir.subtract(b3).multiply(1.2).subtract(red.subtract(b3).multiply(2.5)).multiply(1.5).divide((ee.Image.constant(2.0).multiply(nir).add(1.0)).pow(2.0).subtract(ee.Image.constant(6.0).multiply(nir).subtract(red.sqrt()).multiply(5.0)).subtract(0.5).sqrt()).rename('MTVI2')
    elif (type == 'R'):
        vi = nir.divide(red).rename('RVI')
    elif (type == 'WDR'):
        vi = nir.multiply(0.1).subtract(red).divide(nir.multiply(0.1).add(red)).rename('WDRVI')


    # Mask out clouds and shadows
    vi = vi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean xNDVI for the field polygon
    id = '' if id == None else str(id)
    return vi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()[type + 'VI' + id]


def calculate_exogenous_organic_matter_index(image, date, polygon, id):
    '''
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
    '''
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
        b4 = image.select('B4')
        eomi = ((b11.subtract(b8a)).add(b12.subtract(b4))).divide(b11.add(b8a).add(b12).add(b4)).rename('EOMI3')
    if (id == 4):
        eomi = image.normalizedDifference(['B11', 'B4']).rename('EOMI4')

    # Mask out clouds and shadows
    eomi = eomi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean EOMI for the field polygon
    return eomi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['EOMI' + str(id)]


def calculate_normalized_burn_ratio(image, date, polygon, id=None):
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
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the NBR to be calculated (default is the standard version).
    
    Returns:
        float: the mean NBR2 value, for the specified date and polygon.
    '''
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
    id = '' if id == None else str(id)
    return nbr.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['NBR' + id]


def calculate_chlorophyll_index(image, date, polygon, id):
    '''
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
    '''
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


def calculate_green_coverage_index(image, date, polygon):
    '''
    Calculate the Green Coverage Index (GCI) for a specific date and polygon in a Sentinel-2 image collection.
    
    GCI is a vegetation index that is designed to be less sensitive to atmospheric and soil background effects. It can 
    be used to estimate the fractional green vegetation cover in a given area.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the GCI, for the specified date and polygon.
    '''
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


def calculate_soil_composition_index(image, date, polygon):
    '''
    Calculates the Soil Composition Index (SCI) for a specified date and polygon in a Sentinel-2 image collection.
    
    The Soil Composition Index (SCI) is a measure of soil composition that is useful for identifying areas with high 
    mineral content, such as desert environments. It is calculated as (B11 - B8) / (B11 + B8).
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: The mean value of the Soil Composition Index (SCI) for the specified date and polygon.
    '''
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


def calculate_normalized_difference_red_edge(image, date, polygon, id):
    '''
    Calculates the Normalized Difference Red Edge (NDRE) index for a given image, date, and polygon.

    The Normalized Difference Red Edge (NDRE) is a vegetation index used to assess plant chlorophyll and nitrogen
    content. NDRE is sensitive to the presence of healthy, green vegetation and is useful for monitoring crop health,
    stress, and growth.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the NDRE to be calculated (from 1 to 3).

    Returns:
        float: the calculated NDREx value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate NDRE
    if (id == 1):
        ndre = image.normalizedDifference(['B8', 'B5']).rename('NDRE1')
    elif (id == 2):
        ndre = image.normalizedDifference(['B8', 'B6']).rename('NDRE2')
    elif (id == 3):
        ndre = image.normalizedDifference(['B8', 'B7']).rename('NDRE3')

    # Mask out clouds and shadows
    ndre = ndre.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean NDRE for the field polygon
    return ndre.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['NDRE' + str(id)]


def calculate_modified_chlorophyll_absorption_reflectance_index(image, date, polygon, id=None):
    '''
    Calculates the Modified Chlorophyll Absorption in Reflectance Index (MCARI, MCARI1, MCARI2) for a given image, date, and polygon.

    MCARI is a vegetation index used to estimate chlorophyll content in vegetation, and is based on the difference between the 
    green and red reflectances, weighted by the green reflectance. MCARI1 and MCARI2 are modified versions of MCARI, with different 
    weighting factors for the green and red reflectances.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        id (int): The id of the MCARI index to be calculated (from 0 to 2 - default None).

    Returns:
        float: the calculated MCARI value, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate MCARI (different with respect to the passed id)
    if (id == None):
        mcari = ((image.select('B5').subtract(image.select('B4'))).subtract(image.select('B5').subtract(image.select('B3').multiply(0.2)))).multiply(image.select('B5').divide(image.select('B4'))).rename('MCARI')
    elif (id == 1):
        mcari = ee.Image.constant(1.2).multiply((image.select('B8').subtract(image.select('B4')).multiply(2.5)).subtract(image.select('B8').subtract(image.select('B3')).multiply(1.3))).rename('MCARI1')
    elif (id == 2):
        b4 = image.select('B4')
        b8 = image.select('B8')
        b3 = image.select('B3')
        mcari = (b8.subtract(b4).multiply(2.5)).subtract(b8.subtract(b3).multiply(1.3)).multiply(1.5).divide(((b8.multiply(2.0)).add(1.0)).pow(2).subtract((b8.multiply(6.0)).subtract((b4.multiply(5.0)).sqrt())).subtract(0.5)).rename('MCARI2')

    # Mask out clouds and shadows
    mcari = mcari.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean MCARI for the field polygon
    id = '' if id == None else str(id)
    return mcari.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['MCARI' + id]
   

def calculate_chlorophyll_absorption_ratio_index(image, date, polygon, id):
    '''
    Calculates the Chlorophyll Absorption Ratio Index (CARI) for a given image, date, and polygon.

    The Chlorophyll Absorption Ratio Index (CARI) is a vegetation index used to estimate the amount of chlorophyll
    content in vegetation. It is calculated using the ratio of the near-infrared (NIR) and red (RED) bands of Sentinel-2,
    as well as the blue (BLUE) and green (GREEN) bands.

    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        id (int): The id of the CARI index to be calculated (from 1 to 2).

    Returns:
        float: the calculated CARI value, for the specified date and polygon.
    '''

    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Calculate CARI
    if (id == 1):
        cari = image.select('B5').divide(image.select('B4')) \
                .multiply((ee.Image(((image.select('B5').subtract(image.select('B3'))).divide(150.0)).multiply(670.0)).add(image.select('B4')).add((image.select('B3')).subtract((image.select('B5').subtract(image.select('B3'))).divide(150.0)).multiply(550.0))).pow(2).sqrt()) \
                .divide(((image.select('B5').subtract(image.select('B3'))).divide(150.0).pow(2).add(1)).pow(0.5)) \
                .rename('CARI1')
    elif (id == 2):
        cari = ee.Image(((image.select('B5').subtract(image.select('B3'))).divide(150.0)).multiply(image.select('B4')).add(image.select('B4')).add(image.select('B3')).subtract(ee.Image(0.496).multiply(image.select('B3')))).abs() \
                .divide((ee.Image(0.496).pow(2).add(1)).pow(0.5)) \
                .multiply(image.select('B5').divide(image.select('B4'))) \
                .rename('CARI2')
        
    # Mask out clouds and shadows
    cari = cari.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean CARI for the field polygon
    return cari.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['CARI' + str(id)]


def calculate_bare_soil_index(image, date, polygon):
    '''
    Calculate the Bare Soil Index (BSI) for a specific date and polygon in a Sentinel-2 image collection.
    
    BSI is a vegetation index that can be used to estimate the percentage of bare soil in a given area.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the BSI, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b2 = image.select('B2')
    b4 = image.select('B4')
    b8 = image.select('B8')
    b11 = image.select('B11')

    # Calculate the BSI
    bsi = ((b11.add(b4)).subtract(b8.add(b2))).divide((b11.add(b4)).add(b8.add(b2))).rename('BSI')

    # Mask out clouds and shadows
    bsi = bsi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean BSI for the field polygon
    return bsi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['BSI']


def calculate_green_leaf_index(image, date, polygon):
    '''
    Calculate the Green Leaf Index (GLI) for a specific date and polygon in a Sentinel-2 image collection.
    
    GLI is a vegetation index that is designed to be less sensitive to atmospheric and soil background effects. It can 
    be used to estimate the fractional green vegetation cover in a given area.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the GLI, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b2 = image.select('B2')
    b3 = image.select('B3')
    b4 = image.select('B4')

    # Calculate the GLI
    gli = b3.multiply(2.0).subtract(b4).subtract(b2).divide(b3.multiply(2.0).add(b4).add(b2)).rename('GLI')

    # Mask out clouds and shadows
    gli = gli.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean vegetation index for the field polygon
    return gli.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['GLI']


def calculate_alteration_index(image, date, polygon):
    '''
    Calculate the Alteration index for a specific date and polygon in a Sentinel-2 image collection.
    
    Alteration index is used to map the presence of Al-OH or Fe-OH minerals in rocks, and is particularly useful in 
    mapping alteration zones around ore deposits.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the Alteration index, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b11 = image.select('B11')
    b12 = image.select('B12')

    # Calculate the Alteration index
    alteration = b11.divide(b12).rename('ALTERATION')

    # Mask out clouds and shadows
    alteration = alteration.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean Alteration index for the field polygon
    return alteration.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['ALTERATION']


def calculate_swir_difference_index(image, date, polygon):
    '''
    Calculate the SWIR Difference Index (SDI) for a specific date and polygon in a Sentinel-2 image collection.
    
    SDI is a band ratio index that highlights moisture content and can be used to monitor changes in vegetation
    moisture content, soil moisture, and mineralogical composition.
    
    Args:
        image (ee.ImageCollection): The Sentinel 2 image collection filtered by date and bounds.
        date (pd.Timestamp): The acquisition date in Pandas Timestamp format.
        polygon (ee.Geometry): The field polygon geometry in Earth Engine format.
    
    Returns:
        float: the mean value of the SDI, for the specified date and polygon.
    '''
    # Filter image collection to get the image for the date
    image = ee.Image(image.filterDate(date.strftime('%Y-%m-%d'), (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')).first())

    # Select useful bands
    b8 = image.select('B8')
    b12 = image.select('B12')

    # Calculate the SWIR Difference Index (SDI)
    sdi = b8.subtract(b12).rename('SDI')

    # Mask out clouds and shadows
    sdi = sdi.updateMask(image.select('QA60').bitwiseAnd(2).neq(2))

    # Calculate the mean SDI for the field polygon
    return sdi.reduceRegion(reducer=ee.Reducer.mean(), geometry=polygon).getInfo()['SDI']