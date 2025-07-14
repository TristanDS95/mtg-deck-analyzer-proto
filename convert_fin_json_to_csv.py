import json
import csv
import os

# Load the JSON file
with open("data/fin_cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

# Output file
output_csv_path = "data/fin_scryfall_data.csv"

# Extracted card rows
rows = []

for card in cards:
    if card.get("digital", False) or "CardBack" in card.get("name", ""):
        continue

    name = card.get("name", "")
    mana_cost = card.get("mana_cost", "")
    cmc = card.get("cmc", "")
    type_line = card.get("type_line", "")
    image_url = card.get("image_uris", {}).get("normal", "")
    oracle_text = card.get("oracle_text", "").replace("\n", " ")  # Flatten to 1 line

    rows.append([name, mana_cost, cmc, type_line, oracle_text, image_url])

# Column headers
headers = ["name", "mana_cost", "cmc", "type_line", "oracle_text", "image_url"]

# Write to CSV
with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ Converted {len(rows)} cards to {output_csv_path}")
