import pandas as pd, scipy.stats, matplotlib.pyplot as plt


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
        s_df (pandas DataFrame): A data object containing sentinel-1 or sentinel-2 features extracted
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
        
        # Get the indices of the rows that are between 0 and 30 days after the manure date (why 30 days? Because the effects
        # of fertilization on crop field can be seen not just the day immediately after, but also for few weeks after)
        # https://www.mdpi.com/2072-4292/13/9/1616
        manure_indices = (s_df['crop_field_name'] == field_name) & ((pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date'], format='%Y-%m-%d') - manure_dates[0]).dt.days <= 30) & ((pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date'], format='%Y-%m-%d') - manure_dates[0]).dt.days >= 0)
        
        # Calculate the mean of the valid rows
        mean_df = s_df[~manure_indices].select_dtypes(include=['number']).mean()
        
        # Calculate the normalized difference between the mean and the first values of the manure_indices
        norm_var_df = pd.DataFrame(s_df[manure_indices].select_dtypes(include=['number']).sub(mean_df).div(mean_df).iloc[0].rename('normalized_variation'))
        
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


def display_features_trends(s_df, fields_pos, features, features_pos, sentinel):
    '''
    This function plots the trends of selected features for selected crop fields

    Parameters:
        s_df (pandas DataFrame): A DataFrame containing Sentinel-1 or Sentinel-2 features extracted.
        fields_pos (tuple): A tuple containing the start and end position of the crop field names to plot.
        features (list): A list of feature names to plot.
        features_pos (tuple): A tuple containing the start and end position of the features to plot.
        sentinel (int): The Sentinel number (1 for Sentinel-1 or 2 for Sentinel-2).
    '''
    # Iterate over each crop field name
    for crop_field_name in s_df['crop_field_name'].unique()[fields_pos[0]: fields_pos[-1]]:
        # Create a new plot
        plt.figure()
        legend = []
        
        # Iterate over each feature to plot
        for feature in features[features_pos[0]: features_pos[-1]]:
            # Plot the feature values for the crop field
            plt.plot(s_df[s_df['crop_field_name'] == crop_field_name]['s' + str(sentinel) +'_acquisition_date'], 
                     s_df[s_df['crop_field_name'] == crop_field_name][feature])
            legend.append(feature)
        
        # Add a legend to the plot
        plt.legend(legend)
        
        # Get the manure application dates for the crop field
        manure_date = s_df[s_df['crop_field_name'] == crop_field_name]['manure_dates'].unique()
        
        # Set the plot title, x-axis label, and y-axis label
        plt.title('Trend of features more impacted by manure\nCrop field name: ' + str(crop_field_name) + ' - Manure dates: ' + str(manure_date))
        plt.xlabel('Acquisition date')
        plt.ylabel('Feature value')
        
        # Rotate the x-axis ticks
        plt.xticks(rotation=90)