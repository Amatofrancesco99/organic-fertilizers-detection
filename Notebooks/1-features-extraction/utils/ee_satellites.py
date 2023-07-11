import ee, pandas as pd, concurrent.futures, sentinel1, sentinel2, landsat8


''' GATHER ALL MEAN INDICES FOR A FIELD, FOR EACH TIME A SATELLITE CONSTELLATION (SENTINEL 1, SENTINEL 2 or LANDSAT 8)
CROSSED THE FIELD, WITHIN A SPECIFIC TIME SPAN '''

def process_chunk(s_filtered, chunk, polygon, field_col_name, field_name, satellite):
    '''
    Processes a chunk of acquisition dates for a given polygon and returns a list of acquisitions.
    
    Parameters:
        s_filtered (ee.ImageCollection): A data object with filtered and pre-processed Sentinel-1, Sentinel-2 or Landsat-8 images.
        chunk (pd.Timestamp list): A list of acquisition dates to process.
        polygon (ee.Geometry): The polygon of interest.
        field_col_name (str): The name of the "field_name" column inside the original DataFrame.
        field_name (str): The name of the field.
        satellite (str): The satellite name ("sentinel-1", "sentinel-2" or "landsat-8").
    
    Returns:
        acquisitions (list): A list of dictionaries, where each dictionary represents an acquisition and contains the 
        acquisition date and associated features.
    '''
    acquisitions = []
    for date in chunk:
        if (satellite == 'sentinel-1'):
            polarizations_means = sentinel1.get_all_polarizations(s_filtered, date, polygon)
            ave = sentinel1.calculate_simple_index(polarizations_means, 'AVE')
            dif = sentinel1.calculate_simple_index(polarizations_means, 'DIF')
            rat1 = sentinel1.calculate_simple_index(polarizations_means, 'RAT1')
            rat2 = sentinel1.calculate_simple_index(polarizations_means, 'RAT2')
            ndi = sentinel1.calculate_normalized_difference_index(polarizations_means)
            rvi = sentinel1.calculate_radar_vegetation_index(polarizations_means)

            # Create a dataframe row for the date
            df_acquisition= {str(field_col_name): field_name, 's1_acquisition_date': date,
                        'VV': polarizations_means['VV'], 'VH': polarizations_means['VH'], 
                        'AVE': ave, 'DIF': dif, 'RAT1': rat1, 'RAT2': rat2, 
                        'NDI': ndi, 'RVI': rvi}
        
        elif (satellite == 'sentinel-2'):
            # Calculate standard bands
            bands_means = sentinel2.get_all_bands(s_filtered, date, polygon)
            # Calculate vegetation indexes
            ndvi = sentinel2.calculate_vegetation_index(bands_means, 'ND')
            nsndvi = sentinel2.calculate_vegetation_index(bands_means, 'NSND')
            gndvi = sentinel2.calculate_vegetation_index(bands_means, 'GND')
            rendvi1 = sentinel2.calculate_vegetation_index(bands_means, 'REND', 1)
            rendvi2 = sentinel2.calculate_vegetation_index(bands_means, 'REND', 2)
            rendvi3 = sentinel2.calculate_vegetation_index(bands_means, 'REND', 3)
            grndvi = sentinel2.calculate_vegetation_index(bands_means, 'GRND')
            gbndvi = sentinel2.calculate_vegetation_index(bands_means, 'GBND')
            savi = sentinel2.calculate_vegetation_index(bands_means, 'SA')
            osavi = sentinel2.calculate_vegetation_index(bands_means, 'OSA')
            msavi = sentinel2.calculate_vegetation_index(bands_means, 'MSA')
            tsavi = sentinel2.calculate_vegetation_index(bands_means, 'TSA')
            atsavi = sentinel2.calculate_vegetation_index(bands_means, 'ATSA')
            rvi = sentinel2.calculate_vegetation_index(bands_means, 'R')
            dvi = sentinel2.calculate_vegetation_index(bands_means, 'D')
            cvi = sentinel2.calculate_vegetation_index(bands_means, 'C')
            ctvi = sentinel2.calculate_vegetation_index(bands_means, 'CT')
            avi = sentinel2.calculate_vegetation_index(bands_means, 'A')
            arvi1 = sentinel2.calculate_vegetation_index(bands_means, 'AR', 1)
            arvi2 = sentinel2.calculate_vegetation_index(bands_means, 'AR', 2)
            evi1 = sentinel2.calculate_vegetation_index(bands_means, 'E', 1)
            evi2 = sentinel2.calculate_vegetation_index(bands_means, 'E', 2)
            evi3 = sentinel2.calculate_vegetation_index(bands_means, 'E', 3)
            wdrvi = sentinel2.calculate_vegetation_index(bands_means, 'WDR')
            mtvi1 = sentinel2.calculate_vegetation_index(bands_means, 'MT', 1)
            mtvi2 = sentinel2.calculate_vegetation_index(bands_means, 'MT', 2)
            # Calculate exogenous organic matter indexes
            eomi1 = sentinel2.calculate_exogenous_organic_matter_index(bands_means, 1)
            eomi2 = sentinel2.calculate_exogenous_organic_matter_index(bands_means, 2)
            eomi3 = sentinel2.calculate_exogenous_organic_matter_index(bands_means, 3)
            eomi4 = sentinel2.calculate_exogenous_organic_matter_index(bands_means, 4)
            # Calculate normalized burn ratio indexes
            nbr = sentinel2.calculate_normalized_burn_ratio(bands_means)
            nbr2 = sentinel2.calculate_normalized_burn_ratio(bands_means, 2)
            # Calculate clorophyl indexes
            ci1 = sentinel2.calculate_chlorophyll_index(bands_means, 1)
            ci2 = sentinel2.calculate_chlorophyll_index(bands_means, 2)
            ci3 = sentinel2.calculate_chlorophyll_index(bands_means, 3)
            # Calculate green coverage index
            gci = sentinel2.calculate_green_coverage_index(bands_means)
            # Calculate soil composition index
            sci = sentinel2.calculate_soil_composition_index(bands_means)
            # Calculate normalized difference red edge
            ndre1 = sentinel2.calculate_normalized_difference_red_edge(bands_means, 1)
            ndre2 = sentinel2.calculate_normalized_difference_red_edge(bands_means, 2)
            ndre3 = sentinel2.calculate_normalized_difference_red_edge(bands_means, 3)
            # Calculate chlorophyll absorption ratio index
            cari1 = sentinel2.calculate_chlorophyll_absorption_ratio_index(bands_means, 1)
            cari2 = sentinel2.calculate_chlorophyll_absorption_ratio_index(bands_means, 2)
            # Calculate modified chlorophyll absorption in reflectance index
            mcari = sentinel2.calculate_modified_chlorophyll_absorption_reflectance_index(bands_means)
            mcari1 = sentinel2.calculate_modified_chlorophyll_absorption_reflectance_index(bands_means, 1)
            mcari2 = sentinel2.calculate_modified_chlorophyll_absorption_reflectance_index(bands_means, 2)
            # Calculate bare soil index
            bsi = sentinel2.calculate_bare_soil_index(bands_means)
            # Calculate green leaf index
            gli = sentinel2.calculate_green_leaf_index(bands_means)
            # Compute alteration index
            alteration = sentinel2.calculate_alteration_index(bands_means)
            # Compute SWIR Difference Index
            sdi = sentinel2.calculate_swir_difference_index(bands_means)

            # Create a dataframe row for the date
            df_acquisition= {str(field_col_name): field_name, 's2_acquisition_date': date, 
                        'B1': bands_means['B1'], 'B2': bands_means['B2'], 'B3': bands_means['B3'], 'B4': bands_means['B4'], 'B5': bands_means['B5'],
                        'B6': bands_means['B6'], 'B7': bands_means['B7'], 'B8': bands_means['B8'], 'B8A': bands_means['B8A'], 'B9': bands_means['B9'],
                        'B11': bands_means['B11'], 'B12': bands_means['B12'],     
                        'NDVI': ndvi, 'NSNDVI': nsndvi, 'GNDVI': gndvi, 'RENDVI1': rendvi1, 'RENDVI2': rendvi2,
                        'RENDVI3': rendvi3, 'GRNDVI': grndvi, 'GBNDVI': gbndvi,
                        'SAVI': savi, 'OSAVI': osavi, 'MSAVI': msavi, 'TSAVI': tsavi, 'ATSAVI': atsavi,
                        'RVI': rvi, 'DVI': dvi, 'CVI': cvi, 'CTVI': ctvi, 'AVI': avi, 'ARVI1': arvi1, 'ARVI2': arvi2,
                        'EVI1': evi1, 'EVI2': evi2, 'EVI3': evi3, 'WDRVI': wdrvi, 'MTVI1': mtvi1, 'MTVI2': mtvi2,
                        'EOMI1': eomi1, 'EOMI2': eomi2, 'EOMI3': eomi3, 'EOMI4': eomi4, 
                        'NBR': nbr, 'NBR2': nbr2,
                        'CI1': ci1, 'CI2': ci2, 'CI3': ci3,
                        'GCI': gci, 'SCI': sci, 'NDRE1': ndre1, 'NDRE2': ndre2, 'NDRE3': ndre3,
                        'CARI1': cari1, 'CARI2': cari2, 'MCARI': mcari, 'MCARI1': mcari1, 'MCARI2': mcari2,
                        'BSI': bsi, 'GLI': gli, 'ALTERATION': alteration, 'SDI': sdi}
        
        if (satellite == 'landsat-8'):
            bands_means = landsat8.get_all_bands(s_filtered, date, polygon)

            # Create a dataframe row for the date
            df_acquisition= {str(field_col_name): field_name, 'l8_acquisition_date': date,
                        'B1': bands_means['B1'], 'B2': bands_means['B2'], 'B3': bands_means['B3'],
                        'B4': bands_means['B4'], 'B5': bands_means['B5'], 'B6': bands_means['B6'],
                        'B7': bands_means['B7'], 'B8': bands_means['B8'], 'B9': bands_means['B9'],
                        'B10': bands_means['B10'], 'B11': bands_means['B11']}
            
        # Add row to the list
        acquisitions.append(df_acquisition)

    return acquisitions


def parallelize_features_read(s_filtered, date_range, polygon, field_col_name, field_name, satellite, already_occupied_threads):
    '''
    Reads Sentinel-1, Sentinel-2 or Landsat-8 images and gathers spectral features.
    Furthermore, it makes multiple I/O requests to GEE in parallel - otherwise to compute the same task would have taken too much
    time. Each thread works on different date chunks, maintaining fixed the field.

    Parameters:
        s_filtered (ee.ImageCollection): A data object with filtered and pre-processed Sentinel-1, Sentinel-2 or Landsat-8 images.
        date_range (pd.Timestamp list): A list of acquisition dates to process.
        polygon (ee.Geometry): The polygon of interest.
        field_col_name (str): The name of the "field_name" column inside the original DataFrame.
        field_name (str): The name of the field.
        satellite (str): The satellite name ("sentinel-1", "sentinel-2" or "landsat-8").
        already_occupied_threads (int): The number of threads dedicated to parallelization over the field level.
        
    Returns:
        acquisitions (list): A list of dictionaries, where each dictionary represents an acquisition and contains the 
        acquisition date and associated features.
    '''
    # Split date range into multiple chunks
    ThreadPoolExecutor = concurrent.futures.ThreadPoolExecutor()
    num_chunks = ThreadPoolExecutor._max_workers - already_occupied_threads
    chunk_size = len(date_range) // num_chunks
    date_chunks = [date_range[i:i+chunk_size] for i in range(0, len(date_range), chunk_size)]

    # Create threads to process date chunks in parallel
    acquisitions = []
    # Each thread works on a different chunks of dates to gather features
    with concurrent.futures.ThreadPoolExecutor(num_chunks) as executor:
        futures = []
        for chunk in date_chunks:
            futures.append(executor.submit(process_chunk, s_filtered, chunk, polygon, field_col_name, field_name, satellite))
                
        # Wait for all futures to complete and gather results
        for future in concurrent.futures.as_completed(futures):
            acquisitions.extend(future.result())

    return acquisitions


def process_field(field, start_date, end_date, satellite, filters_params, already_occupied_threads):
    '''
    Processes a single field by calculating the mean indices for each time the satellite passed over that field.

    Args:
        field (pandas Dataframe - row): The field item containing the field name and polygon coordinates.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.
        satellite (str): The satellite name ("sentinel-1", "sentinel-2" or "landsat-8").
        filters_params (list): The list of parameters to be used for filters parameters for extracting satellite Images Collections.
        already_occupied_threads (int): The number of threads dedicated to parallelization over the field level.

    Returns:
        list: A list of dictionary objects containing the mean calculated indices for each acquisition date, for the
        specified field (using the selected satellite).
    '''
    # Get the field name and polygon coordinates
    field_name = field[0]
    polygon = ee.Geometry.Polygon(field[1])
    
    if (satellite == 'sentinel-1'):
        # Filter Sentinel 1 collection
        s_collection = ee.ImageCollection('COPERNICUS/S1_GRD')
        s_filtered = s_collection.filterBounds(polygon).filterDate(str(start_date), str(end_date)) \
                                    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                                    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
                                    .filter(ee.Filter.eq('instrumentMode', 'IW')) \
                                    .filter(ee.Filter.eq('orbitProperties_pass', filters_params[0])) #\
                                    #.filter(ee.Filter.eq('relativeOrbitNumber_start', 66)) \
                                    #.filterMetadata('resolution_meters', 'equals', 10)
    elif (satellite == 'sentinel-2'):
        # Filter Sentinel 2 collection
        s_collection = ee.ImageCollection('COPERNICUS/S2_SR')
        s_filtered = s_collection.filterBounds(polygon).filterDate(str(start_date), str(end_date)) \
                                .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', int(filters_params[0])))
    elif (satellite == 'landsat-8'):
        # Filter Landsat 8 collection
        s_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
        s_filtered = s_collection.filterBounds(polygon).filterDate(str(start_date), str(end_date))
        
    # Get distinct dates from the satellite Image collection and put into the date_range list
    s_dates = s_filtered.aggregate_array('system:time_start').map(lambda time_start: ee.Date(time_start).format('YYYY-MM-dd'))
    s_dates_distinct = s_dates.distinct().sort()
    date_range = pd.to_datetime(s_dates_distinct.getInfo())
    
    return parallelize_features_read(s_filtered, date_range, polygon, field.index[0], field_name, satellite, already_occupied_threads)


def get_features(fields_df, start_date, end_date, satellite, filters_params=None, fields_threads=4):
    '''
    It allows to get from a pandas DataFrame composed of crop fields information, another DataFrame that contains 
    for each time a satellite (sentinel-1, sentinel-2 or landsat-8) passed on regions of interest, within a given time period, 
    all the mainly used features mean values (optical, radar or thermal).
    Furthermore, it makes multiple I/O requests to Google Earth Engine (GEE) in parallel - otherwise to compute the same task 
    would have taken too much time. Each thread works on different date chunks, maintaining fixed the field (obviously if you
    have only one field this part is not parallelized).
    Please consider that parallelization of requests has been applied on two levels: on fields and on dates.

    Args:
        fields_df (pandas DataFrame): A DataFrame containing the crop field name and polygon coordinates for each field.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.
        satellite (str): The satellite name ("sentinel-1": radar, "sentinel-2": optical, "landsat-8": optical + thermal).
        filters_params (list - default `None`): The list of parameters values to be used for filters to extracting satellite Images Collections.
            * For Sentinel-1:
                * first parameter in the list rapresents the value of the 'orbitProperties_pass' filter ('ASCENDING' or 'DESCENDING')
            * For Sentinel-2:
                * first parameter in the list represents the value of the 'CLOUDY_PIXEL_PERCENTAGE' filter ('LTE' - values in range [0, 100])
        fields_threads (int - default `4`): The number of threads to dedicate to parallelization of requests over the fields level, the remaining part 
            instead is used to apply parallelization over dates level. The value of this parameter should be high (with respect 
            to the overall number of threads exploitable) if you have a lot of crop fields but a little time-span to consider, whereas
            if you have fewer fields but a bigger time-span you should decrease this parameter.
            Finally, if you have lot of fields with lot of dates to process it should may be optimal considering half of the 
            overall number of threads available.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the calculated indices for each acquisition date, for each field within
        the specified date range and using the selected satellite. The DataFrame includes columns for the crop 
        details, acquisition date and calculated indices. The calculated indices depend on the selected satellite.
    '''
    # Create an empty list to store the data for each field
    df_list = []

    # Calculate all the indices for each field, for the selected time period
    # In parallell, to improve performances (each thread works on one single field)
    with concurrent.futures.ThreadPoolExecutor(fields_threads) as executor:
        futures = []
        # When just one field is inside the fields_df DataFrame
        if (len(fields_df) == 2):
            futures.append(executor.submit(process_field, fields_df, start_date, end_date, satellite, filters_params, fields_threads))
        else:
            for index, field in fields_df.iterrows():
                futures.append(executor.submit(process_field, field, start_date, end_date, satellite, filters_params, fields_threads))
                
        # Wait for all futures to complete and gather results
        for future in concurrent.futures.as_completed(futures):
            df_list.extend(future.result())

    # Create a dataframe from the list of rows
    df = pd.DataFrame(df_list).reset_index(drop=True)
    
    # Sorting by crop field name and acquisition date and return the sorted DataFrame
    return df.sort_values([str(df.columns[0]), str(df.columns[1])], ascending=[True, True])