# mtg-deck-analyzer-proto

Web app project using streamlit; 

For Magic: The Gathering Card game (specifically Final Fantasy Set)

Process:
- Starts with parsers - input string of drafted cards (copy and paste list from MTGA or 17Lands)
- Pulls card data using Scryfall
- Pulls card ratings from 17lands spreadsheet
- Uses this card data and card rating data in deck_logic;
  - color eval - determins best color pairing based on highest avg rating with largest volume of available colors
  - card scorer - then takes those color pairings and adds additional scoring logic for each cards (curve considerations/castability/etc)
  - deck_builder - assembles the chosen cards into a functional deck (minus lands)
- The deck is then fed back into the main app.py
      
