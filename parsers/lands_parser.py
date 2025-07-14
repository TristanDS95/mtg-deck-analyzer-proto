import pandas as pd
from io import StringIO


def parse_17lands(csv_text):

    df = pd.read_csv(StringIO(csv_text))

    name_col = 'Name' if 'Name' in df.columns else 'Card Name'
    count_col = 'Quantity' if 'Quantity' in df.columns else 'Count'

    df = df[[name_col, count_col]]
    df.columns = ['name', 'count']

    return df.to_dict(orient='records')


