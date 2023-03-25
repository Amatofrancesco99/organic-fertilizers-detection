import ee, pandas as pd, concurrent.futures, optical_features, radar_features


""" GATHER ALL MEAN INDICES FOR A FIELD, FOR EACH TIME SENTINEL (SENTINEL 1 or SENTINEL 2) SATELLITES 
CROSSED THE FIELD, WITHIN A SPECIFIC TIME SPAN """

def s2_process_field(field, start_date, end_date):
    """
    Processes a single field by calculating the mean indices for each time the satellite (sentinel 2)
    passed over that field.

    Args:
        field (pandas Dataframe - row): The field item containing the field name, and polygon coordinates.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.

    Returns:
        list: A list of dictionary objects containing the mean calculated indices for each acquisition date, for the
        specified field (using the selected sentinel satellite).
    """
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
        # Calculate s1 indices for the date
        ndvi = optical_features.calculate_ndvi(s2_filtered, date, polygon)
        eomi1 = optical_features.calculate_eomi(s2_filtered, date, polygon, 1)
        eomi2 = optical_features.calculate_eomi(s2_filtered, date, polygon, 2)
        eomi3 = optical_features.calculate_eomi(s2_filtered, date, polygon, 3)
        eomi4 = optical_features.calculate_eomi(s2_filtered, date, polygon, 4)
        nbr2 = optical_features.calculate_nbr2(s2_filtered, date, polygon)
        savi = optical_features.calculate_savi(s2_filtered, date, polygon)
        msavi = optical_features.calculate_savi(s2_filtered, date, polygon, 'M')

        # Create a dataframe row for the date
        df_acquisition= {str(field.index[0]): field_name, 's2_acquisition_date': date, 'NDVI': ndvi,
                    'EOMI1': eomi1, 'EOMI2': eomi2, 'EOMI3': eomi3, 'EOMI4': eomi4, 'NBR2': nbr2,
                    'SAVI': savi, 'MSAVI': msavi}
        
        # Add row to the list
        acquisitions.append(df_acquisition)
    
    return acquisitions


def s1_process_field(field, start_date, end_date):
    """
    Processes a single field by calculating the mean indices for each time the satellite (sentinel 1)
    passed over that field.

    Args:
        field (pandas Dataframe - row): The field item containing the field name and polygon coordinates.
        start_date (str): The start date of the date range to filter the collection by.
        end_date (str): The end date of the date range to filter the collection by.

    Returns:
        list: A list of dictionary objects containing the mean calculated indices for each acquisition date, for the
        specified field (using the selected sentinel satellite).
    """
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
    """
    Takes a pandas DataFrame of fields information, a start date, an end date, and a sentinel integer as inputs, 
    and returns a pandas DataFrame of calculated indices for each field and acquisition date within the specified
    date range, using the selected sentinel satellite.
    Furthermore, it works in parallel in order to exploit the entire computational power of the machine on which you are
    running this function (load balanced the work of each core) - otherwise to compute the same task would have taken too much
    time.

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
    """
    # Create an empty list to store the data for each field
    df_list = []

    # Calculate all the indices for each field, for the selected time period
    # In parallell, to improve performances (each core works on one single field)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for index, field in fields_df.iterrows():
            futures.append(executor.submit(s1_process_field if sentinel == 1 else s2_process_field, 
                                           field, start_date, end_date))
        
        # Wait for all futures to complete and gather results
        for future in concurrent.futures.as_completed(futures):
            df_list.extend(future.result())

        # Create a dataframe from the list of rows
        return pd.DataFrame(df_list)