import pandas as pd, scipy.stats, matplotlib.pyplot as plt, numpy as np
from sklearn.preprocessing import MinMaxScaler


def get_MinMaxScaled_df(s_df, feature_range):
    '''
    This function applies MinMax scaling to the pandas DataFrame passed as parameter, to all the numeric columns 
    having values not already ranging between the specified feature range.

    Parameters:
        s_df (pandas DataFrame): A data object containing sentinel-1 or sentinel-2 features extracted.
        feature_range (tuple): A tuple containing the values that you want your scaled features will range (e.g. (-1, 1)).
        
    Returns:
        pandas DataFrame: A DataFrame containing the columns of the original DataFrame scaled (the numerical ones, not already
        ranging within the specified feature range).
    '''
    # Define the scaler Object
    scaler = MinMaxScaler(feature_range = feature_range)

    numeric_cols = s_df.select_dtypes(include=np.number).columns.tolist()

    # Iterate over the numeric columns and scale only the ones that have values outside of the 
    # feature_range specified range
    s_df_norm = s_df.copy()
    for col in numeric_cols:
        if (s_df_norm[col].min() < feature_range[0]) or (s_df_norm[col].max() > feature_range[1]):
            s_df_norm[col] = scaler.fit_transform(s_df_norm[[col]])
    
    # Return the scaled DataFrame
    return s_df_norm


def get_features_importance(s_df, sentinel, hide_plain=False):
    '''
    This function basically computes a rank that contains the importance of features. The more the features (on average, considering
    different crop fields and different manure dates) have been changed with respect to the yearly trend, when manure has not been
    applied, the higher the importance.
    In so doing we can understand which are the features that have been mostly impacted by fertilization.
    A metric to perform the feature importance has been defined in terms of absolute normalized variation, that is to say:
        feature_importance = abs((feature_value[manured].mean() - feature_value[~manured].mean()) / feature_value[~manured].mean())
    Furthermore a T-Test has been applied in order to understand how many times occurred that the feature importance was higher then
    0, considering different manure dates and many crop fields. 

    Parameters:
        s_df (pandas DataFrame): A data object containing sentinel-1 or sentinel-2 features extracted.
        sentinel (int): The sentinel number (1 for Sentinel-1 or 2 for Sentinel-2).
        hide_plain (boolean): Whether to consider the plain features (for Sentinel-1 are polarizations, while for
        Sentinel-2 are bands).
        
    Returns:
        pandas DataFrame: A DataFrame containing the importance of each feature (for each feature we have its own
        absolute normalized variation, aka importance, the t-statistic and p-value), sorted by importance (descending order).
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
        
        # Calculate the mean for the rows where manure have not been applied
        mean_df = s_df[~manure_indices].select_dtypes(include=['number']).mean()
        
        # Calculate the importance of features by means of the difference of the mean value when manure has been applied 
        # (considered just two dates after the fertilization date - the date immediately after manure can be a noisy estimate, so
        # it is better averaging on two dates...) and when not, divided by the latter one
        importance_df = pd.DataFrame(s_df[manure_indices].select_dtypes(include=['number']).sub(mean_df).div(mean_df).iloc[0:2].mean().rename('importance'))
        
        # Calculate the absolute features importance and sort by descending order
        abs_importance_df = importance_df.abs().sort_values(by=importance_df.columns[0], ascending=False).reset_index().rename(columns={"index": "feature"})

        # Remove plain features (if explicitly asked)
        if (hide_plain):
            if (sentinel == 1):
                # Remove the plain polarizations values since we do not want to consider those
                abs_importance_df = abs_importance_df.drop(abs_importance_df[abs_importance_df['feature'].isin(['VV', 'VH'])].index)
            if (sentinel == 2):
                # Remove the plain bands values since we do not want to consider those
                abs_importance_df = abs_importance_df.drop(abs_importance_df[abs_importance_df['feature'].isin(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'])].index)
        
        # Add the results to the list
        results_list.append(abs_importance_df)

    # Concatenate the results for all fields into a single dataframe and rank by descending order by feature importance
    results_df = pd.concat(results_list).groupby('feature').mean().sort_values(by='importance', ascending=False)

    # Calculate the p-value and the t_statistic for each feature. The objective is basically to measure the significance 
    # of the importance for each feature, considering different crop fields (the more the number of times a crop field had 
    # a higher importance value - absolute standardized variation - when manure has been applied, the higher the t-statistic
    # and the lower the p-value).
    # ttest_1samp doc = https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html
    t_statistics, p_values = [], []
    for feature in results_df.index:
        t_stat, p_val = scipy.stats.ttest_1samp(pd.concat(results_list).groupby('feature').get_group(str(feature))['importance'], 0)
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