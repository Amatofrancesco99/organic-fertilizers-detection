import ee, pandas as pd, concurrent.futures, optical_features, radar_features


''' GATHER ALL MEAN INDICES FOR A FIELD, FOR EACH TIME SENTINEL (SENTINEL 1 or SENTINEL 2) SATELLITES 
CROSSED THE FIELD, WITHIN A SPECIFIC TIME SPAN '''

def s2_process_field(field, start_date, end_date):
    '''
    Processes a single field by calculating the mean indices for each time the satellite (sentinel 2)
    passed over that field.

    Args:
        field (pandas Dataframe - row): The field item containing the field name, and polygon coordinates.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.

    Returns:
        list: A list of dictionary objects containing the mean calculated indices for each acquisition date, for the
        specified field (using the selected sentinel satellite).
    '''
    # Get the field name and polygon coordinates
    field_name = field[0]
    polygon = ee.Geometry.Polygon(field[1])
    
    # Filter Sentinel 2 collection
    s2_collection = ee.ImageCollection('COPERNICUS/S2_SR')
    s2_filtered = s2_collection.filterBounds(polygon).filterDate(str(start_date), str(end_date)) \
                                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))

    # Get distinct dates from the Sentinel 2 collection and put into the date_range list
    s2_dates = s2_filtered.aggregate_array('system:time_start').map(lambda time_start: ee.Date(time_start).format('YYYY-MM-dd'))
    s2_dates_distinct = s2_dates.distinct().sort()
    date_range = pd.to_datetime(s2_dates_distinct.getInfo())
    
    # Create a list to store rows for the field
    acquisitions = []
    for date in date_range:
        # Calculate standard bands
        b1 = optical_features.get_band(s2_filtered, date, polygon, '1')
        b2 = optical_features.get_band(s2_filtered, date, polygon, '2')
        b3 = optical_features.get_band(s2_filtered, date, polygon, '3')
        b4 = optical_features.get_band(s2_filtered, date, polygon, '4')
        b5 = optical_features.get_band(s2_filtered, date, polygon, '5')
        b6 = optical_features.get_band(s2_filtered, date, polygon, '6')
        b7 = optical_features.get_band(s2_filtered, date, polygon, '7')
        b8 = optical_features.get_band(s2_filtered, date, polygon, '8')
        b8a = optical_features.get_band(s2_filtered, date, polygon, '8A')
        b9 = optical_features.get_band(s2_filtered, date, polygon, '9')
        b11 = optical_features.get_band(s2_filtered, date, polygon, '11')
        b12 = optical_features.get_band(s2_filtered, date, polygon, '12')
        # Calculate vegetation indexes
        ndvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'ND')
        nsndvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'NSND')
        gndvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'GND')
        rendvi1 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'REND', 1)
        rendvi2 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'REND', 2)
        rendvi3 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'REND', 3)
        grndvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'GRND')
        gbndvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'GBND')
        savi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'SA')
        osavi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'OSA')
        msavi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'MSA')
        tsavi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'TSA')
        atsavi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'ATSA')
        rvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'R')
        dvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'D')
        cvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'C')
        ctvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'CT')
        avi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'A')
        arvi1 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'AR', 1)
        arvi2 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'AR', 2)
        evi1 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'E', 1)
        evi2 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'E', 2)
        evi3 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'E', 3)
        wdrvi = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'WDR')
        mtvi1 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'MT', 1)
        mtvi2 = optical_features.calculate_vegetation_index(s2_filtered, date, polygon, 'MT', 2)
        # Calculate exogenous organic matter indexes
        eomi1 = optical_features.calculate_exogenous_organic_matter_index(s2_filtered, date, polygon, 1)
        eomi2 = optical_features.calculate_exogenous_organic_matter_index(s2_filtered, date, polygon, 2)
        eomi3 = optical_features.calculate_exogenous_organic_matter_index(s2_filtered, date, polygon, 3)
        eomi4 = optical_features.calculate_exogenous_organic_matter_index(s2_filtered, date, polygon, 4)
        # Calculate normalized burn ratio indexes
        nbr = optical_features.calculate_normalized_burn_ratio(s2_filtered, date, polygon)
        nbr2 = optical_features.calculate_normalized_burn_ratio(s2_filtered, date, polygon, 2)
        # Calculate clorophyl indexes
        ci1 = optical_features.calculate_chlorophyll_index(s2_filtered, date, polygon, 1)
        ci2 = optical_features.calculate_chlorophyll_index(s2_filtered, date, polygon, 2)
        ci3 = optical_features.calculate_chlorophyll_index(s2_filtered, date, polygon, 3)
        # Calculate green coverage index
        gci = optical_features.calculate_green_coverage_index(s2_filtered, date, polygon)
        # Calculate soil composition index
        sci = optical_features.calculate_soil_composition_index(s2_filtered, date, polygon)
        # Calculate normalized difference red edge
        ndre1 = optical_features.calculate_normalized_difference_red_edge(s2_filtered, date, polygon, 1)
        ndre2 = optical_features.calculate_normalized_difference_red_edge(s2_filtered, date, polygon, 2)
        ndre3 = optical_features.calculate_normalized_difference_red_edge(s2_filtered, date, polygon, 3)
        # Calculate chlorophyll absorption ratio index
        cari1 = optical_features.calculate_chlorophyll_absorption_ratio_index(s2_filtered, date, polygon, 1)
        cari2 = optical_features.calculate_chlorophyll_absorption_ratio_index(s2_filtered, date, polygon, 2)
        # Calculate modified chlorophyll absorption in reflectance index
        mcari = optical_features.calculate_modified_chlorophyll_absorption_reflectance_index(s2_filtered, date, polygon)
        mcari1 = optical_features.calculate_modified_chlorophyll_absorption_reflectance_index(s2_filtered, date, polygon, 1)
        mcari2 = optical_features.calculate_modified_chlorophyll_absorption_reflectance_index(s2_filtered, date, polygon, 2)
        # Calculate bare soil index
        bsi = optical_features.calculate_bare_soil_index(s2_filtered, date, polygon)
        # Calculate green leaf index
        gli = optical_features.calculate_green_leaf_index(s2_filtered, date, polygon)
        # Compute alteration index
        alteration = optical_features.calculate_alteration_index(s2_filtered, date, polygon)
        # Compute SWIR Difference Index
        sdi = optical_features.calculate_swir_difference_index(s2_filtered, date, polygon)

        # Create a dataframe row for the date
        df_acquisition= {str(field.index[0]): field_name, 's2_acquisition_date': date, 
                    'B1': b1, 'B2': b2, 'B3': b3, 'B4': b4, 'B5': b5, 'B6': b6, 'B7': b7,
                    'B8': b8, 'B8A': b8a, 'B9': b9, 'B11': b11, 'B12': b12,     
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
        
        # Add row to the list
        acquisitions.append(df_acquisition)
    
    return acquisitions


def s1_process_field(field, start_date, end_date):
    '''
    Processes a single field by calculating the mean indices for each time the satellite (sentinel 1)
    passed over that field.

    Args:
        field (pandas Dataframe - row): The field item containing the field name and polygon coordinates.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.

    Returns:
        list: A list of dictionary objects containing the mean calculated indices for each acquisition date, for the
        specified field (using the selected sentinel satellite).
    '''
    # Get the field name and polygon coordinates
    field_name = field[0]
    polygon = ee.Geometry.Polygon(field[1])
    
    # Filter Sentinel 1 collection
    s1_collection = ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT')
    s1_filtered = s1_collection.filterBounds(polygon).filterDate(str(start_date), str(end_date)) \
                                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) \
                                .filter(ee.Filter.eq('instrumentMode', 'IW')) \
                                .filterMetadata('resolution_meters', 'equals', 10)

    # Get distinct dates from the Sentinel 1 collection and put into the date_range list
    s1_dates = s1_filtered.aggregate_array('system:time_start').map(lambda time_start: ee.Date(time_start).format('YYYY-MM-dd'))
    s1_dates_distinct = s1_dates.distinct().sort()
    date_range = pd.to_datetime(s1_dates_distinct.getInfo())
    
    # Create a list to store rows for the field
    acquisitions = []
    for date in date_range:
        # Calculate s1 indices for the date
        bsi = radar_features.calculate_bsi(s1_filtered, date, polygon)
        pbsi = radar_features.calculate_bsi(s1_filtered, date, polygon, 'P')
        cpbsi = radar_features.calculate_bsi(s1_filtered, date, polygon, 'CP')
        tirs = radar_features.calculate_tirs(s1_filtered, date, polygon)

        # Create a dataframe row for the date
        df_acquisition= {str(field.index[0]): field_name, 's1_acquisition_date': date,
                    'BSI': bsi, 'PBSI': pbsi, 'CPBSI': cpbsi, 'TIRS': tirs}
        
        # Add row to the list
        acquisitions.append(df_acquisition)
    
    return acquisitions


def get_features(fields_df, start_date, end_date, sentinel):
    '''
    Takes a pandas DataFrame of fields information, a start date, an end date, and a sentinel integer as inputs, 
    and returns a pandas DataFrame of calculated indices for each field and acquisition date within the specified
    date range, using the selected sentinel satellite.
    Furthermore, it works in parallel in order to exploit the entire computational power of the machine on which you are
    running this function (load balanced the work of each core) - otherwise to compute the same task would have taken too much
    time. Each core works on a different field (obviously if you have only one field this code cannot be parallelized)

    Args:
        fields_df (pandas DataFrame): A DataFrame containing the crop field name and polygon coordinates for each field.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.
        sentinel (int): The type of sentinel satellite to use (1 = radar, 2 = optical).

    Returns:
        pd.DataFrame: A pandas DataFrame containing the calculated indices for each acquisition date, for each field within
        the specified date range and using the selected sentinel satellite. The DataFrame includes columns for the crop 
        details, acquisition date and calculated indices. The calculated indices depend on the selected
        sentinel.
    '''
    # Create an empty list to store the data for each field
    df_list = []

    # Calculate all the indices for each field, for the selected time period
    # In parallell, to improve performances (each core works on one single field)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        # When just one field is inside the fields_df DataFrame
        if (len(fields_df) == 2):
            futures.append(executor.submit(s1_process_field if sentinel == 1 else s2_process_field, 
                                                fields_df, start_date, end_date))
        else:
            for index, field in fields_df.iterrows():
                futures.append(executor.submit(s1_process_field if sentinel == 1 else s2_process_field, 
                                                field, start_date, end_date))
                
        # Wait for all futures to complete and gather results
        for future in concurrent.futures.as_completed(futures):
            df_list.extend(future.result())

    # Create a dataframe from the list of rows
    return pd.DataFrame(df_list)