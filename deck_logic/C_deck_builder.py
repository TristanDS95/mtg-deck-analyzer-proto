import pandas as pd

from deck_logic.b_card_scorer import score_card, compute_castability_penalty, compute_curve_bonus


def build_deck(df, color_pair, target_curve=None, num_main_deck_cards=23, total_deck_size=40):
    if target_curve is None:
        target_curve = {1: 1, 2: 5, 3: 4, 4: 4, 5: 3, 6: 2, 7: 1}

    df = df.copy()
    df['color_id'] = df['Color'].apply(lambda c: ''.join(sorted(set(str(c).upper()))))
    df_playable = df[df['color_id'].apply(lambda cid: set(cid).issubset(set(color_pair)))]
    df_playable = df_playable.dropna(subset=['GIH WR'])

    main_deck = pd.DataFrame()
    current_curve = {}
    main_deck_count = 0  # total actual cards added

    while main_deck_count < num_main_deck_cards and not df_playable.empty:
        df_playable['score'] = df_playable.apply(
        lambda row: score_card(row, current_curve, target_curve, color_pair),
        axis=1
    )
    top_card = df_playable.sort_values(by='score', ascending=False).iloc[0:1].copy()

    card_count = int(top_card.iloc[0].get('count', 1))
    allowed_count = min(card_count, num_main_deck_cards - main_deck_count)
    top_card.at[top_card.index[0], 'count'] = allowed_count
    index = top_card.index[0]


    # Safely parse and update curve
    cmc_value = top_card.iloc[0]['cmc'] if 'cmc' in top_card.columns else 0
    try:
        cmc = int(float(cmc_value))
    except (ValueError, TypeError):
        cmc = 0
    cmc = min(cmc, 7)
    current_curve[cmc] = current_curve.get(cmc, 0) + allowed_count

    # Add to main deck
    main_deck = pd.concat([main_deck, top_card], ignore_index=True)
    main_deck_count += allowed_count

    # Reduce count or drop row
    if card_count > allowed_count:
        df_playable.at[index, 'count'] = card_count - allowed_count
    else:
        df_playable = df_playable.drop(index)


    # Estimate land counts based on mana symbols in main_deck
    from collections import Counter
    color_counts = Counter()
    for _, row in main_deck.iterrows():
        mana_cost = str(row.get('mana_cost', ''))
        for symbol in 'WUBRG':
            color_counts[symbol] += mana_cost.count(symbol)

    total_symbols = sum(color_counts[c] for c in color_pair)
    land_counts = {}
    for color in color_pair:
        land_counts[color] = round((color_counts[color] / total_symbols) * (total_deck_size - len(main_deck))) if total_symbols > 0 else (total_deck_size - len(main_deck)) // len(color_pair)

    basic_lands = {'W': 'Plains', 'U': 'Island', 'B': 'Swamp', 'R': 'Mountain', 'G': 'Forest'}
    land_rows = [{'name': basic_lands[color], 'count': count, 'type_line': 'Basic Land', 'Color': color} for color, count in land_counts.items()]
    lands_df = pd.DataFrame(land_rows)

    final_deck = pd.concat([main_deck, lands_df], ignore_index=True)
    sideboard = df_playable

    print(f"[DEBUG] Returning main_deck with {main_deck['count'].sum()} cards and {len(main_deck)} unique entries")

    return main_deck, lands_df, df_playable





