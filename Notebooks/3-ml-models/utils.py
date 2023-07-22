import pandas as pd, numpy as np, time, pickle
from sklearn.utils import resample
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score


def get_modified_df(s_df, satellite):
    '''
    This function modifies the input DataFrame, such that we obtain the difference between two consequent acquisitions, for a 
    specific crop field and a further column named 'y' indicating whether a manure date is within the two considered consequent
    acquisitions.

    Parameters:
        s_df (pandas DataFrame): A data object containing features extracted from a satellite.
        satellite (str): The satellite name abbreviated ('s1' for Sentinel-1, 's2' for Sentinel-2, or 'l8' for Landsat-8).

    Returns:
        pandas DataFrame: The modified DataFrame with the additional 'y' column.
    '''
    # Create a copy of the passed DataFrame
    s_df_orig = s_df.copy()

    # Convert the xx_acquisition_date column to datetime (where 'xx' is the satellite name abbreviated)
    acq_date_col_name = str(satellite) + '_acquisition_date'
    s_df_orig[acq_date_col_name] = pd.to_datetime(s_df_orig[acq_date_col_name])

    # Calculate the difference between consecutive dates grouped by crop_field_name
    s_df_mod = s_df_orig.groupby('crop_field_name').apply(lambda x: x.drop(columns=[acq_date_col_name, 'manure_dates']).apply(lambda y: y.diff() if y.name != 'crop_field_name' else y))

    # Add a column that contains the string representation of the date difference between two
    # consequent_xx_acquisition_date values for a specific crop field
    s_df_mod['consequent_' + str(satellite) + '_acquisitions'] = s_df_orig.groupby('crop_field_name')[acq_date_col_name].apply(lambda x: ['[{}, {}]'.format(x.iloc[i].strftime('%Y-%m-%d'), x.iloc[i+1].strftime('%Y-%m-%d')) for i in range(-1, len(x)-1)]).explode().reset_index(drop=True)
    # Add column manure_dates that is the same of the original dataframe
    s_df_mod['manure_dates'] = s_df_orig['manure_dates']

    # Add a column y that contains 1 if one of the manure dates is within two consequent_xx_acquisition_date for a specific crop field,
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
    s_df_mod = s_df_mod[['crop_field_name', 'consequent_' + str(satellite) + '_acquisitions'] + [col for col in s_df_mod.columns if col not in ['crop_field_name', 'consequent_' + str(satellite) + '_acquisitions', 'manure_dates', 'y']] + ['manure_dates', 'y']]

    # Return the dataframe and removes NaN rows
    return s_df_mod.dropna().reset_index(drop=True)


def get_balanced_df(s_df_mod, method, random_state=0):
    """
    Returns a balanced dataframe where the number of 0's and 1's are equal for each unique crop field (exploiting oversampling
    or undersampling methods).

    Args:
        s_df_mod (pandas DataFrame): The original dataframe to balance.
        method (str): The method to be used to sample the dataset ('under' or 'over').
        random_state (int): The random seed to use for sampling (default 0).

    Returns:
        pandas DataFrame: A balanced dataframe where the number of 0's and 1's are equal for each unique crop field.
    """
    # Get the unique crop field names
    crop_fields = s_df_mod['crop_field_name'].unique()

    # Initialize an empty list to store the restricted dataframes for each crop field
    restricted_dfs = []

    # Loop over each crop field
    for crop_field in crop_fields:
        if (method == 'under'):
            # Get the rows where y = 1 and crop_field_name is equal to the current crop field
            manured_cf_df = s_df_mod[(s_df_mod['y'] == 1) & (s_df_mod['crop_field_name'] == crop_field)]

            # Get the rows where y = 0 and crop_field_name is equal to the current crop field
            not_manured_cf_df = s_df_mod[(s_df_mod['y'] == 0) & (s_df_mod['crop_field_name'] == crop_field)]

            # Sample the same number of rows from the not_manured_cf_df as there are in the manured_cf_df
            not_manured_cf_downsampled_df = not_manured_cf_df.sample(n=len(manured_cf_df), random_state=random_state)

            # Append the restricted dataframe for the current crop field to the list of restricted dataframes
            restricted_dfs.append(pd.concat([manured_cf_df, not_manured_cf_downsampled_df]))
        
        elif (method == 'over'):
            # Get the rows where y = 1 and crop_field_name is equal to the current crop field
            manured_cf_df = s_df_mod[(s_df_mod['y'] == 1) & (s_df_mod['crop_field_name'] == crop_field)]

            # Get the rows where y = 0 and crop_field_name is equal to the current crop field
            not_manured_cf_df = s_df_mod[(s_df_mod['y'] == 0) & (s_df_mod['crop_field_name'] == crop_field)]

            # Oversample the minority class (y = 1)
            manured_cf_oversampled_df = resample(manured_cf_df, n_samples=len(not_manured_cf_df), random_state=random_state)

            # Append the restricted dataframe for the current crop field to the list of restricted dataframes
            restricted_dfs.append(pd.concat([not_manured_cf_df, manured_cf_oversampled_df]))

    # Concatenate all of the restricted dataframes into a single balanced dataframe
    restricted_df = pd.concat(restricted_dfs)

    # Return the balanced dataframe
    return restricted_df.sort_values(by=[s_df_mod.columns[0], s_df_mod.columns[1]]).reset_index(drop=True)


def measure_scv_performances(X, y, model, scaler=None, n_folds=5, random_state=0, save=False):
    '''
    This function performs Stratified Cross-Validation for a given model and scaler using the KFold method, and returns a 
    DataFrame containing mean accuracy, precision, recall and f1-score for both train and test sets. It also prints a summary
    of the model, scaler, number of KFolds and elapsed time.

    Parameters:
        X (pandas DataFrame): The input features to be used for stratified cross-validation.
        y (pandas Series): The target variable to be used for stratified cross-validation.
        model (sklearn estimator): The model to be trained and tested using stratified cross-validation.
        scaler (sklearn scaler): The scaler to be used to normalize the features (default None).
        n_folds (int): The number of folds to be used for stratified cross-validation (default 5).
        random_state (int): The random state to be used for the KFold object (default 0).
        save (boolean): Whether to save the obtained model and scaler, for later use (default False).

    Returns:
        pandas DataFrame: a DataFrame containing the different performance metrics results, considering the passed parameters.
    '''
    # Define the stratified-cross-validation object
    kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    # Initialize lists to store the results for each fold
    train_acc, test_acc = [], []
    train_prec, test_prec = [], []
    train_rec, test_rec = [], []
    train_f1, test_f1 = [], []

    start_time = time.time()

    for train_index, test_index in kf.split(X, y):
        # Normalize the train folds (if scaler not None)
        X_train = X.iloc[train_index] if scaler == None else scaler.fit_transform(X.iloc[train_index])
        y_train = y.iloc[train_index]
        
        # Fit the logistic regression model
        model.fit(X_train, y_train)
        
        # Normalize the test fold (if scaler not None)
        X_test = X.iloc[test_index] if scaler == None else scaler.transform(X.iloc[test_index])
        y_test = y.iloc[test_index]

        # Predict the classes for the train and test fold
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate the evaluation metrics for the train and test fold
        train_acc.append(accuracy_score(y_train, y_pred_train))
        test_acc.append(accuracy_score(y_test, y_pred_test))

        train_prec.append(precision_score(y_train, y_pred_train, average='weighted', zero_division=0))
        test_prec.append(precision_score(y_test, y_pred_test, average='weighted', zero_division=0))

        train_rec.append(recall_score(y_train, y_pred_train, average='weighted', zero_division=0))
        test_rec.append(recall_score(y_test, y_pred_test, average='weighted', zero_division=0))

        train_f1.append(f1_score(y_train, y_pred_train, average='weighted', zero_division=0))
        test_f1.append(f1_score(y_test, y_pred_test, average='weighted', zero_division=0))

    # Save the last model and scaler (if asked)
    if (save):
        pickle.dump(model, open('saved-config/model.pkl', 'wb'))
        pickle.dump(scaler, open('saved-config/scaler.pkl', 'wb'))
    
    # Print the details
    print('Summary: ' + str(model) + ', ' + str(scaler) + ', ' + str(n_folds) + ' KFolds' + ', ' + str(round((time.time() - start_time), 3)) + 's\n')
    
    # Create a DataFrame containing performance metrics results
    performances_df = pd.DataFrame.from_dict({
        'Dataset': ['Train', 'Test'],
        'Mean Accuracy': [round(np.mean(train_acc), 2), round(np.mean(test_acc), 2)],
        'Mean Precision': [round(np.mean(train_prec), 2), round(np.mean(test_prec), 2)],
        'Mean Recall': [round(np.mean(train_rec), 2), round(np.mean(test_rec), 2)],
        'Mean F1': [round(np.mean(train_f1), 2), round(np.mean(test_f1), 2)]
    }).set_index(keys='Dataset')

    # Return the performances DataFrame
    return performances_df