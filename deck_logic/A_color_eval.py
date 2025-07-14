# deck_logic/color_eval.py

from collections import defaultdict
import itertools
import pandas as pd

# List of MTG colors
COLORS = ['W', 'U', 'B', 'R', 'G']

def get_color_identity(color_str):
    """
    Normalize a color string into a sorted identity like 'WU' or 'BGR'.
    Handles cards with multiple colors.
    """
    if not isinstance(color_str, str):
        return ''
    identity = ''.join(sorted(set(color_str.upper())))
    return identity

def suggest_color_pairs(df, min_cards_per_pair=8):
    """
    Suggest the best color pairs based on number of cards and total GIH WR.
    
    Parameters:
    - df: DataFrame containing 'Color' and 'GIH WR' columns
    - min_cards_per_pair: Minimum playable cards needed to consider the color pair

    Returns:
    - List of tuples: (color_pair, num_cards, avg_wr, total_wr)
    """
    # Normalize color identity
    df = df.copy()
    df['color_id'] = df['Color'].apply(get_color_identity)

    # Generate all 2-color pairs
    color_pairs = [''.join(sorted(pair)) for pair in itertools.combinations(COLORS, 2)]

    results = []

    for pair in color_pairs:
        playable = df[df['color_id'].apply(lambda cid: all(c in pair for c in cid))]
        num_cards = len(playable)
        if num_cards < min_cards_per_pair:
            continue
        avg_wr = playable['GIH WR'].mean()
        total_wr = playable['GIH WR'].sum()
        results.append((pair, num_cards, avg_wr, total_wr))

    # Sort by total_wr then avg_wr
    results.sort(key=lambda x: (x[3], x[2]), reverse=True)
    return results

# if __name__ == "__main__":
#     import pandas as pd

#     # Load a sample dataset for testing (adjust path as needed)
#     try:
#         df = pd.read_csv("data/merged_sample.csv")  # or use df_merged
#     except FileNotFoundError:
#         print("Test CSV not found. Please ensure you have a test file.")
#         exit()

#     df['GIH WR'] = (
#         df['GIH WR']
#         .astype(str)
#         .str.replace('%', '', regex=False)
#         .str.strip())

#     df['GIH WR'] = pd.to_numeric(df['GIH WR'], errors='coerce')
  
#     print(df.dtypes)
#     print(df[['name', 'GIH WR']].head())
#     print(df['GIH WR'].isna().sum(), "rows have NaN GIH WR")

#     results = suggest_color_pairs(df)

#     print("=== Recommended Color Pairs ===")
#     for pair, count, avg_wr, total_wr in results[:5]:
#         print(f"{pair}: {count} cards | Avg GIH WR: {avg_wr:.2f}")
