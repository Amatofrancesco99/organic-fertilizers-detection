import pandas as pd, numpy as np, time
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, precision_score, recall_score


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
    s_df_orig = s_df.copy()

    # Convert the s2_acquisition_date column to datetime
    acq_date_col_name = 's' + str(sentinel) +'_acquisition_date'
    s_df_orig[acq_date_col_name] = pd.to_datetime(s_df[acq_date_col_name])

    # Convert the manure_dates column to a list of dates
    s_df_orig['manure_dates'] = s_df_orig['manure_dates'].apply(lambda x: pd.to_datetime(eval(x)) if isinstance(x, str) else [])

    # Calculate the absolute difference between consecutive dates grouped by crop_field_name
    s_df_mod = s_df_orig.groupby('crop_field_name', as_index=False).apply(lambda x: x.drop(columns=[acq_date_col_name, 'manure_dates']).apply(lambda y: y.diff().abs() if y.name != 'crop_field_name' else y))

    # Add a column y that contains 1 if one of the manure dates is within two consequent s2_acquisition_date for a specific crop field,
    # otherwise 0
    def check_overlap(df):
        manure_dates = df['manure_dates'].tolist()
        s2_dates = df[acq_date_col_name].tolist()
        results = [np.NAN]
        for j in range(1, len(s2_dates) - 1):
            results.append(0)
            for i in range(len(manure_dates)):
                if (s2_dates[j] < manure_dates[i] <= s2_dates[j+1]):
                    results.append(1)
                    break
        return pd.Series(results)

    # Add the column y
    s_df_mod['y'] = s_df_orig.groupby('crop_field_name').apply(check_overlap).reset_index(drop=True)

    # Return the dataframe and removes NaN rows
    return s_df_mod.dropna()


def get_balanced_df(s2_df_mod, method, random_state):
    """
    Returns a balanced dataframe where the number of 0's and 1's are equal for each unique crop field.

    Args:
    s2_df_mod (pd.DataFrame): The original dataframe to balance.
    method (str): The method to be used to get the dataset balanced ('under', 'over' or 'combo')
    random_state (int): The random seed to use for sampling.

    Returns:
    pd.DataFrame: A balanced dataframe where the number of 0's and 1's are equal for each unique crop field.
    """

    # Get the unique crop field names
    crop_fields = s2_df_mod['crop_field_name'].unique()

    # Initialize an empty list to store the restricted dataframes for each crop field
    restricted_dfs = []

    if (method == 'under'):
        # Loop over each crop field
        for crop_field in crop_fields:
            # Get the rows where y = 1 and crop_field_name is equal to the current crop field
            manured_cf_df = s2_df_mod[(s2_df_mod['y'] == 1) & (s2_df_mod['crop_field_name'] == crop_field)]

            # Get the rows where y = 0 and crop_field_name is equal to the current crop field
            not_manured_cf_df = s2_df_mod[(s2_df_mod['y'] == 0) & (s2_df_mod['crop_field_name'] == crop_field)]

            # Sample the same number of rows from the not_manured_cf_df as there are in the manured_cf_df
            not_manured_cf_sampled_df = not_manured_cf_df.sample(n=len(manured_cf_df), random_state=random_state)

            # Concatenate the manured_cf_df and the not_manured_cf_sampled_df into a single dataframe for the current crop field
            restricted_cf_df = pd.concat([manured_cf_df, not_manured_cf_sampled_df])

            # Append the restricted dataframe for the current crop field to the list of restricted dataframes
            restricted_dfs.append(restricted_cf_df)

    # Concatenate all of the restricted dataframes into a single balanced dataframe
    restricted_df = pd.concat(restricted_dfs)

    # Sort the balanced dataframe by index
    restricted_df.sort_index(inplace=True)

    # Return the balanced dataframe
    return restricted_df


def measure_scv_performances(X, y, model, scaler=None, n_folds=5, random_state=0):
    '''
    This function performs Stratified Cross-Validation for a given model and scaler using the KFold method, and returns the 
    precision, recall and f1-score for each class. It also prints a summary of the model, scaler, number of 
    KFolds and elapsed time.

    Parameters:
        X (pandas DataFrame): The input features to be used for stratified cross-validation.
        y (pandas Series): The target variable to be used for stratified cross-validation.
        model (sklearn estimator): The model to be trained and tested using stratified cross-validation.
        scaler (sklearn scaler): The scaler to be used to normalize the features.
        n_folds (int): The number of folds to be used for stratified cross-validation.
        random_state (int): The random state to be used for the KFold object.

    Returns:
        None
    '''
    # define the stratified-cross-validation object
    kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    # perform stratified-cross-validation and get the predicted classes for each fold
    y_pred = []
    start_time = time.time()

    for train_index, test_index in kf.split(X, y):
        # normalize the train folds (if scaler not None)
        X_train = X.iloc[train_index] if scaler == None else scaler.fit_transform(X.iloc[train_index])
        y_train = y.iloc[train_index]
        
        # fit the logistic regression model
        model.fit(X_train, y_train)
        
        # normalize the test fold (if scaler not None)
        X_test = X.iloc[test_index] if scaler == None else scaler.fit_transform(X.iloc[test_index])
        
        # predict the classes for the test fold
        y_pred.extend(model.predict(X_test))
    
    end_time = time.time()
    # print the results
    print('-'*100)
    print('Summary: ' + str(model) + ', ' + str(scaler) + ', ' + str(n_folds) + ' KFolds' + ', ' + str(round((end_time - start_time), 3)) + 's (elapsed time)\n')
    print('Class 0 (~Manured) - Precision:', round(precision_score(y, y_pred, pos_label=0), 2), ' - Recall:', round(recall_score(y, y_pred, pos_label=0), 2), ' - F1:', round(f1_score(y, y_pred, pos_label=0), 2))
    print('Class 1 (Manured)  - Precision:', round(precision_score(y, y_pred, pos_label=1), 2), ' - Recall:', round(recall_score(y, y_pred, pos_label=1), 2), ' - F1:', round(f1_score(y, y_pred, pos_label=1), 2))
    print('-'*100)