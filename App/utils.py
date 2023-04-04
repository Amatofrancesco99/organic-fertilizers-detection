import json, pandas as pd


def get_fields_df(json_path):
    '''
    Reads a JSON file containing polygons (fields) and converts it to a Pandas DataFrame ('id', 'name',
    and 'polygon_coordinates').
    
    Parameters:
        json_path (str): The path to the JSON file containing the polygons.
    
    Returns:
    pandas.DataFrame: A DataFrame with the following columns:
        - id (int): The ID of the field.
        - name (str): The name of the field.
        - polygon_coordinates (list of tuples): The coordinates of the vertices of the field polygon.
    '''
    # Load JSON data from file
    with open(json_path) as f:
        data = json.load(f)

    # Create DataFrame with properties excluding 'manure_dates' column
    fields_df = pd.DataFrame([{k:v for k,v in f['properties'].items()} for f in data['features']])

    # Add column with field name for each field
    fields_names = []
    for _id in range(1,  fields_df.shape[0] + 1):
        fields_names.append('P-Test'+str(_id))
    fields_df['crop_field_name'] = fields_names

    # Add column with coordinates for each field
    fields_df['polygon_coordinates'] = [[tuple(c) for c in p] for f in data['features'] for p in f['geometry']['coordinates']]

    # return the pandas DataFrame
    return fields_df