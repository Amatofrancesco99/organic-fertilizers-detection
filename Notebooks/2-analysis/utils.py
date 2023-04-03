import pandas as pd, scipy.stats


def get_normalized_variation(s_df, sentinel):
    '''
    This function basically computes a rank that contains how much the features (on average, considering different crop fields
    and different manure dates) have been changed with respect to the mean value that feature had when manure has not been applied.
    In so doing we can understand which are the features that have been mostly impacted by fertilization.
    In order to do so, the variation has been mesured in terms of absolute normalized variation
        absolute_normalized_variation = abs((mean_feature_value[manured] - mean_feature_value[~manured]) / mean_feature_value[~manured])
    Furthermore a T-Test has been applied in order to understand how many times occurred that the absolute normalized difference
    was higher then 0, considering different manure dates on the crop fields. 

    Parameters:
        s_df (pandas DataFrame): A data object with filtered and pre-processed Sentinel-1 and Sentinel-2 images
        sentinel (int): The sentinel number (1 for Sentinel-1 or 2 for Sentinel-2).
        
    Returns:
        pandas DataFrame: A DataFrame containing the mean absolute normalized variation, the t-statistic and p-value for each
        sentinel extracted feature, sorted by descending order.
    '''
    # Get unique values of the 'crop_field_name' column
    field_names = s_df['crop_field_name'].unique()

    # Create an empty list to store the results for each field
    results_list = []

    # Loop through each field and perform the operations
    for field_name in field_names:
        # Convert manure_dates column to a list of datetimes
        manure_dates = pd.to_datetime(s_df['manure_dates'].apply(lambda x: x.replace("['", "").replace("']", "")), format='%Y-%m-%d')
        
        # Get the indices of the rows that are more between 0 and 30 days after the manure date
        manure_indices = (s_df['crop_field_name'] == field_name) & ((pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date'], format='%Y-%m-%d') - manure_dates[0]).dt.days <= 30) & ((pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date'], format='%Y-%m-%d') - manure_dates[0]).dt.days >= 0)
        
        # Calculate the mean of the valid rows
        mean_df = s_df[~manure_indices].select_dtypes(include=['float', 'int']).mean()
        
        # Calculate the normalized difference between the mean and the first values of the manure_indices
        norm_var_df = pd.DataFrame(s_df[manure_indices].select_dtypes(include=['float', 'int']).sub(mean_df).div(mean_df).iloc[0].rename('normalized_variation'))
        
        # Calculate the absolute normalized difference and sort by descending order
        abs_norm_var_df = norm_var_df.abs().sort_values(by=norm_var_df.columns[0], ascending=False).reset_index().rename(columns={"index": "feature"})

        if (sentinel == 1):
            # Remove the plain polarizations values since we do not want to consider those
            abs_norm_var_df = abs_norm_var_df.drop(abs_norm_var_df[abs_norm_var_df['feature'].isin(['VV', 'VH'])].index)
        if (sentinel == 2):
            # Remove the plain bands values since we do not want to consider those
            abs_norm_var_df = abs_norm_var_df.drop(abs_norm_var_df[abs_norm_var_df['feature'].isin(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'])].index)
        
        # Add the results to the list
        results_list.append(abs_norm_var_df)

    # Concatenate the results for all fields into a single dataframe and rank by descending order for absolute normalized variation
    results_df = pd.concat(results_list).groupby('feature').mean().sort_values(by='normalized_variation', ascending=False)

    # Calculate the p-value and the t_statistic for each feature. The objective is basically to measure the significance 
    # of the absolute normalized variation for each feature, considering different crop fields (the more the number of times
    # a crop field had a higher absolute normalized variation when manure has been applied, the higher the t-statistic and
    # the lower the p-value).
    # ttest_1samp doc = https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html
    t_statistics, p_values = [], []
    for feature in results_df.index:
        t_stat, p_val = scipy.stats.ttest_1samp(pd.concat(results_list).groupby('feature').get_group(str(feature))['normalized_variation'], 0)
        t_statistics.append(t_stat)
        p_values.append(p_val)
    
    # Add to the dataframe the calculated t-stats and p-values
    results_df['t_statistic'] = t_statistics
    results_df['p_value'] = p_values

    # Return the DataFrame
    return results_df