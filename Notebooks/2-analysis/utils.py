import pandas as pd, scipy.stats, matplotlib.pyplot as plt, numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, MaxAbsScaler, RobustScaler


def get_normalized_df(s_df, method, feature_range=(-1, 1)):
    '''
    This function applies a selected normalization method to the pandas DataFrame passed as parameter.

    Parameters:
        s_df (pandas DataFrame): A data object containing features extracted from a satellite.
        method (str): The method to be used in order to normalize the DataFrame (allowed: "min-max", "mean-var", 
        "max-abs", "robust").
        feature_range (tuple): A tuple containing the values that you want your scaled features will range (default: (-1, 1)).
        It works only with "min-max" scaling method.

    Returns:
        pandas DataFrame: A DataFrame containing the columns of the original DataFrame scaled.
    '''
    # Define the scaler Object
    if method == "min-max":
        scaler = MinMaxScaler(feature_range=feature_range)
    elif method == "mean-var":
        scaler = StandardScaler()
    elif method == "max-abs":
        scaler = MaxAbsScaler()
    elif method == "robust":
        scaler = RobustScaler()

    numeric_cols = s_df.select_dtypes(include=np.number).columns.tolist()

    # Iterate over the numeric columns and scale only the ones that have values outside of the 
    # feature_range specified range
    s_df_norm = s_df.copy()
    for col in numeric_cols:
        s_df_norm[col] = scaler.fit_transform(s_df_norm[[col]])
    
    # Return the scaled DataFrame
    return s_df_norm


def get_features_importance(s_df, satellite, hide_plain=False):
    '''
    This function basically computes a rank that contains the importance of features. The more the features (on average, considering
    different crop fields and different manure dates) have been changed with respect to the yearly trend, when manure has not been
    applied, the higher the importance.
    In so doing we can understand which are the features that have been mostly impacted by manure application.
    A metric to perform the feature importance has been defined in terms of:
        feature_importance = abs(feature_val[imm_after_manure] - feature_val[imm_before_manure]) / max(abs(daily_feature_diff[~manure]))
    Furthermore a t-test has been applied in order to understand how many times occurred that the feature importance was higher then
    0, considering different manure dates and many crop fields. 

    Parameters:
        s_df (pandas DataFrame): A data object containing features extracted from a satellite.
        satellite (str): The satellite name abbreviated ('s1' for Sentinel-1, 's2' for Sentinel-2, or 'l8' for Landsat-8).
        hide_plain (boolean): Whether to consider the plain features (for Sentinel-1 are polarizations, while for
        Sentinel-2 and Landsat-8 are standard bands).
        
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
        # Get the fraction of the original dataframe relative to the single crop field
        df = s_df[s_df['crop_field_name'] == field_name]
        # Get the manure date of each crop field (we have just one for each crop field) - Modifications needed if more then one
        # manure dates are present (but this is not the case)
        manure_date = pd.to_datetime(df['manure_dates'].apply(lambda x: x.replace("['", "").replace("']", "")), format='%Y-%m-%d').unique()[0]

        # Get the indices of the rows that are between 0 and 15 days after the manure date (why 15 days? Because the effects
        # of manure application on crop field can be seen not just the day immediately after, but also for few weeks after)
        # https://www.mdpi.com/2072-4292/13/9/1616
        manure_indices =  ((pd.to_datetime(df[str(satellite) + '_acquisition_date'], format='%Y-%m-%d') - manure_date).dt.days >= 0) & ((pd.to_datetime(df[str(satellite) + '_acquisition_date'], format='%Y-%m-%d') - manure_date).dt.days <= 15)
        # Get the indices of the rows before manure date 
        before_manure_indices = (pd.to_datetime(df[str(satellite) + '_acquisition_date'], format='%Y-%m-%d') < manure_date)

        # It calculates the means of the features considering 2 acquisitions before manure date
        mean_prev = df[before_manure_indices].select_dtypes(include=['number']).tail(2).mean()
        # It calculates the differences of features between two consequent acquisitions, for all the times manure has not been applied
        max_daily_diff = df[~manure_indices].select_dtypes(include=['number']).diff().dropna().abs().max()

        # Calculate the importance of features (note that this formula is quite complex)
        # feature_importance = abs(feature_val[imm_after_manure] - feature_val[imm_before_manure]) / max(abs(daily_feature_diff[~manure]))
        importance_df = pd.DataFrame((df[manure_indices].select_dtypes(include=['number']).iloc[0].sub(mean_prev)).abs().div(max_daily_diff).rename('importance'))   
        # Sort the importances
        importance_df = importance_df.sort_values(by=importance_df.columns[0], ascending=False).reset_index().rename(columns={"index": "feature"})

        # Hide plain features (if explicitly asked)
        if (hide_plain):
            if (satellite == 's1'):
                # Remove the polarizations values since we do not want to consider those
                importance_df = importance_df.drop(importance_df[importance_df['feature'].isin(['VV', 'VH'])].index)
            elif (satellite == 's2'):
                # Remove the bands values since we do not want to consider those
                importance_df = importance_df.drop(importance_df[importance_df['feature'].isin(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'])].index)
            elif (satellite == 'l8'):
                # Remove the bands values since we do not want to consider those
                importance_df = importance_df.drop(importance_df[importance_df['feature'].isin(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11'])].index)
        
        # Add the results to the list
        results_list.append(importance_df)

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
    return results_df.reset_index()


def display_features_trends(s_df, fields_pos, features, features_pos, satellite):
    '''
    This function plots the trends of selected features for selected crop fields.

    Parameters:
        s_df (pandas DataFrame): A data object containing features extracted from a satellite.
        fields_pos (tuple): A tuple containing the start and end position of the crop field names to plot.
        features (list): A list of feature names to plot.
        features_pos (tuple): A tuple containing the start and end position of the features to plot.
        satellite (str): The satellite name abbreviated ('s1' for Sentinel-1, 's2' for Sentinel-2, or 'l8' for Landsat-8).
    
    Returns:
        None.
    '''
    # Iterate over each crop field name
    for crop_field_name in s_df['crop_field_name'].unique()[fields_pos[0]: fields_pos[-1]]:
        # Create a new plot
        plt.figure(figsize=(16,5))
        legend = []
        
        # Iterate over each feature to plot
        for feature in features[features_pos[0]: features_pos[-1]]:
            # Plot the feature values for the crop field
            plt.plot(s_df[s_df['crop_field_name'] == crop_field_name][str(satellite) +'_acquisition_date'], 
                     s_df[s_df['crop_field_name'] == crop_field_name][feature])
            legend.append(feature)
        
        # Get the manure application dates for the crop field
        manure_dates = s_df[s_df['crop_field_name'] == crop_field_name]['manure_dates'].unique()

        # Set the plot title, x-axis label, and y-axis label
        plt.title('Trend of features more impacted by manure\nCrop field name: ' + str(crop_field_name) + ' - Manure dates: ' + str(manure_dates))
        plt.xlabel('Acquisition date')
        plt.ylabel('Feature value')

        # Add vertical dashed lines before and after each manure application date
        for manure_date in manure_dates:
            manure_date = pd.to_datetime(manure_date.replace('[','').replace(']',''))
            before_manure_date = s_df[(s_df['crop_field_name'] == crop_field_name) & (pd.to_datetime(s_df[str(satellite) + '_acquisition_date']) < manure_date)][str(satellite) + '_acquisition_date'].iloc[-1]
            after_or_equal_manure_date = s_df[(s_df['crop_field_name'] == crop_field_name) & (pd.to_datetime(s_df[str(satellite) + '_acquisition_date']) >= manure_date)][str(satellite) + '_acquisition_date'].iloc[0]
            plt.axvline(x=before_manure_date, linestyle='--', color='k')
            plt.axvline(x=after_or_equal_manure_date, linestyle='--', color='k')
            legend.append('RoI')
        
        # Add a legend to the plot
        plt.legend(legend)

        # Rotate the x-axis ticks
        plt.xticks(rotation=90)