# deck_logic/card_scorer.py

import pandas as pd

def compute_castability_penalty(mana_cost, color_pair):
    """
    Penalize cards that are harder to cast (e.g., double/triple pips of off-color)
    """
    if not isinstance(mana_cost, str):
        return 0

    penalty = 0
    for color in 'WUBRG':
        count = mana_cost.count(color)
        if color not in color_pair:
            penalty += count * 2  # off-color pips are harsh
        else:
            penalty += max(0, count - 1) * 0.5  # multiple pips are mildly penalized

    return -penalty  # negative = penalty

def compute_curve_bonus(cmc, current_curve, target_curve):
    try:
        cmc = int(float(cmc))  # handle string or float cmc
    except (ValueError, TypeError):
        return 0  # invalid cmc, skip bonus

    cmc = min(cmc, 7)  # cap curve group at 7
    target = target_curve.get(cmc, 0)
    current = current_curve.get(cmc, 0)
    gap = target - current
    return gap * 0.5 if gap > 0 else 0



def score_card(row, current_curve, target_curve, color_pair):
    """
    Score a single card row.
    """
    try:
        base = float(row.get('GIH WR', 0))
    except (ValueError, TypeError):
        base = 0.0

    mana_cost = row.get('mana_cost', '')

    try:
        cmc = float(row.get('cmc', 0))
    except (ValueError, TypeError):
        cmc = 0

    score = base
    score += compute_curve_bonus(cmc, current_curve, target_curve)
    score += compute_castability_penalty(mana_cost, color_pair)

    return score



def score_card_pool(df, target_curve, color_pair):
    """
    Score all cards in a filtered card pool.
    Returns a DataFrame with an added 'score' column.
    """
    df = df.copy()
    current_curve = {}

    scores = []
    for _, row in df.iterrows():
        score = score_card(row, current_curve, target_curve, color_pair)
        scores.append(score)

    df['score'] = scores
    return df.sort_values(by='score', ascending=False)
