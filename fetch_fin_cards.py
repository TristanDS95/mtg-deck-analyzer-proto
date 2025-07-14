import requests
import json
import os

# Ensure 'data/' directory exists
os.makedirs("data", exist_ok=True)

# Scryfall API for FINAL FANTASY (set code FIN)
url = "https://api.scryfall.com/cards/search?q=e%3AFIN&include_extras=false&include_variations=false"
cards = []

print("Fetching cards from Scryfall FIN set...")

while url:
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"❌ Error {resp.status_code}: {resp.text}")
        break

    data = resp.json()
    cards.extend(data["data"])
    url = data.get("next_page")  # Will be None if there are no more pages

print(f"✅ Retrieved {len(cards)} cards.")

# Save to JSON
with open("data/fin_cards.json", "w") as f:
    json.dump(cards, f, indent=2)

print("✅ Saved to data/fin_cards.json")
