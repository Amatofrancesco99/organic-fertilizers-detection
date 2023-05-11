import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, StandardScaler, MaxAbsScaler, RobustScaler


def get_modified_df(s_df, sentinel):
    '''
    This function modifies the input DataFrame, such that we obtain the difference between two consequent acquisitions, for a 
    specific crop field and a further column named 'y' indicating whether a manure date is within the two considered consequent
    acquisitions.

    Parameters:
        s_df (pandas DataFrame): A DataFrame containing Sentinel-1 or Sentinel-2 extracted features.
        sentinel (int): An integer indicating whether the DataFrame contains Sentinel-1 or Sentinel-2 features.

    Returns:
        pandas DataFrame: The modified DataFrame with the additional 'y' column.
    '''
    # Create a copy of the passed DataFrame
    s_df_orig = s_df.copy()

    # Convert the sX_acquisition_date column to datetime
    acq_date_col_name = 's' + str(sentinel) +'_acquisition_date'
    s_df_orig[acq_date_col_name] = pd.to_datetime(s_df_orig[acq_date_col_name])

    # Calculate the difference between consecutive dates grouped by crop_field_name
    s_df_mod = s_df_orig.groupby('crop_field_name').apply(lambda x: x.drop(columns=[acq_date_col_name, 'manure_dates']).apply(lambda y: y.diff() if y.name != 'crop_field_name' else y))

    # Add a column that contains the string representation of the date difference between two
    # consequent s_acquisition_date values for a specific crop field
    s_df_mod['consequent_s' +str(sentinel) + '_acquisitions'] = s_df_orig.groupby('crop_field_name')[acq_date_col_name].apply(lambda x: ['[{}, {}]'.format(x.iloc[i].strftime('%Y-%m-%d'), x.iloc[i+1].strftime('%Y-%m-%d')) for i in range(-1, len(x)-1)]).explode().reset_index(drop=True)
    # Add column manure_dates that is the same of the original dataframe
    s_df_mod['manure_dates'] = s_df_orig['manure_dates']

    # Add a column y that contains 1 if one of the manure dates is within two consequent s_acquisition_date for a specific crop field,
    # otherwise 0
    def check_overlap(crop_df):
        manure_dates = crop_df['manure_dates'].apply(lambda x: pd.to_datetime(eval(x)) if isinstance(x, str) else []).tolist()
        s2_dates = crop_df[acq_date_col_name].tolist()
        results = [np.NAN] + [0] * (len(s2_dates) - 1)
        for j in range(0, len(s2_dates) - 1):
            for i in range(len(manure_dates)):
                if (s2_dates[j] < manure_dates[i] <= s2_dates[j+1]):
                    results[j+1] = 1
                    break
        return pd.Series(results)
    
    # Add the column y
    s_df_mod['y'] = s_df_orig.groupby('crop_field_name').apply(check_overlap).reset_index(drop=True)

    # Rearrange columns order
    s_df_mod = s_df_mod[['crop_field_name', 'consequent_s' +str(sentinel) + '_acquisitions'] + [col for col in s_df_mod.columns if col not in ['crop_field_name', 'consequent_s' +str(sentinel) + '_acquisitions', 'manure_dates', 'y']] + ['manure_dates', 'y']]

    # Return the dataframe and removes NaN rows
    return s_df_mod.dropna().reset_index(drop=True)


def get_normalized_df(s_df, method, feature_range=(-1, 1)):
    '''
    This function applies a selected normalization method to the pandas DataFrame passed as parameter.

    Parameters:
        s_df (pandas DataFrame): A data object containing Sentinel-1 or Sentinel-2 features extracted.
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


def display_features_trends(s_df, fields_pos, features, features_pos, sentinel):
    '''
    This function plots the trends of selected features for selected crop fields.

    Parameters:
        s_df (pandas DataFrame): A DataFrame containing Sentinel-1 or Sentinel-2 features extracted.
        fields_pos (tuple): A tuple containing the start and end position of the crop field names to plot.
        features (list): A list of feature names to plot.
        features_pos (tuple): A tuple containing the start and end position of the features to plot.
        sentinel (int): The Sentinel number (1 for Sentinel-1 or 2 for Sentinel-2).
    
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
            plt.plot(s_df[s_df['crop_field_name'] == crop_field_name]['s' + str(sentinel) +'_acquisition_date'], 
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
            before_manure_date = s_df[(s_df['crop_field_name'] == crop_field_name) & (pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date']) < manure_date)]['s' + str(sentinel) + '_acquisition_date'].iloc[-1]
            after_or_equal_manure_date = s_df[(s_df['crop_field_name'] == crop_field_name) & (pd.to_datetime(s_df['s' + str(sentinel) + '_acquisition_date']) >= manure_date)]['s' + str(sentinel) + '_acquisition_date'].iloc[0]
            plt.axvline(x=before_manure_date, linestyle='--', color='k')
            plt.axvline(x=after_or_equal_manure_date, linestyle='--', color='k')
            legend.append('RoI')
        
        # Add a legend to the plot
        plt.legend(legend, loc='upper right')

        # Rotate the x-axis ticks
        plt.xticks(rotation=90)