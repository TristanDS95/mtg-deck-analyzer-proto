import streamlit as st
import pandas as pd
from parsers.lands_parser import parse_17lands
from parsers.mtga_parser import parse_mtga
from deck_logic.A_color_eval import suggest_color_pairs
from deck_logic.C_deck_builder import build_deck


st.set_page_config(page_title="Deck Analyzer", layout="wide")
st.title("TEST - MTG Deck Analyzer")

uploaded_file = st.file_uploader("Upload your card pool (MTGA.txt or 17Lands csv)", type=["txt","csv"])

st.markdown("### Or Paste your card pool directly below:")
pasted_text = st.text_area("Paste card pool here - MTGA or 17Lands")

card_pool = None
source = None

if pasted_text.strip():
      file_text = pasted_text
      card_pool = parse_mtga(file_text)
      source = "Clipboard"

# Choose parser based on file type
elif uploaded_file is not None:
    file_name = uploaded_file.name
    file_text = uploaded_file.read().decode("utf-8")

    if uploaded_file.name.endswith(".txt"):
            st.text(file_text)
            card_pool = parse_mtga(file_text)
            source = "MTGA (file)"
    elif uploaded_file.name.endswith(".csv"):
            card_pool = parse_17lands(file_text)
            source = "17Lands (file)"
    else:
            st.error("Please Upload txt or csv file")
            st.stop()

if card_pool is None:
    st.info("Awaiting File Upload or Paste Input")

if card_pool is not None:
    with st.expander("Debug: Raw card pool", expanded=False):
        st.write(card_pool)
#maybe add card art/formatting to make more visually appealing






# Load 17Lands data
try:
    lands_data = pd.read_csv("data/fin_card_data.csv")
except FileNotFoundError:
    st.error("Missing 17Lands data. Place fin_card_data.csv in /data")
    st.stop()

# Load enriched Scryfall data
try:
    scryfall_data = pd.read_csv("data/fin_scryfall_data.csv")
except FileNotFoundError:
    st.error("Missing Scryfall data. Place fin_scryfall_data.csv in /data")
    st.stop()

    # Convert card_pool to DataFrame
if card_pool is not None:
    df_pool = pd.DataFrame(card_pool)


    # Normalize 'card' or 'Card' to 'name'
    if "card" in df_pool.columns:
        df_pool = df_pool.rename(columns={"card": "name"})
    elif "Card" in df_pool.columns:
        df_pool = df_pool.rename(columns={"Card": "name"})

    # Strip whitespace from column names
    df_pool.columns = df_pool.columns.astype(str).str.strip()
    lands_data.columns = lands_data.columns.astype(str).str.strip()

    # Clean whitespace
    df_pool["name"] = df_pool["name"].str.strip()
    lands_data["Name"] = lands_data["Name"].str.strip()
    scryfall_data["name"] = scryfall_data["name"].str.strip()

    # Merge with 17Lands
    merged_17lands = pd.merge(df_pool, lands_data, left_on="name", right_on="Name", how="left")

    # Merge with Scryfall data
    df_merged = pd.merge(merged_17lands, scryfall_data, on="name", how="left")


    # Save merged pool for TESTING LOGIC MODS
    # df_merged.to_csv("data/merged_sample.csv", index=False)


    # Show merged table
    st.subheader("📊 Pool with Ratings & Metadata")
    st.dataframe(
    df_merged[['name', 'count', 'Color', 'GIH WR', 'cmc', 'mana_cost', 'type_line']]
    .sort_values(by="GIH WR", ascending=False)
    )




#     WORK IN PROGRESS - CARD POOL VISUALIZER
    st.markdown("---")
    st.subheader("🖼️ Visual Deck: Cards by Color")

    if 'Color' not in df_merged.columns or 'image_url' not in df_merged.columns:
        st.warning("Missing color or image URL data. Ensure your CSV includes 'Color' and 'image_url'.")
    else:
        color_names = {
            'W': 'White',
            'U': 'Blue',
            'B': 'Black',
            'R': 'Red',
            'G': 'Green',
            'M': 'Multicolor',
            'C': 'Colorless',
        }

        def get_color_group(color_str):
            if not isinstance(color_str, str):
                return 'C'
            colors = ''.join(sorted(set(color_str.upper())))
            if len(colors) == 1:
                return colors
            elif len(colors) > 1:
                return 'M'
            else:
                return 'C'

        df_merged['color_group'] = df_merged['Color'].apply(get_color_group)
        color_order = ['W', 'U', 'B', 'R', 'G', 'M', 'C']

        for color in color_order:
            group_df = df_merged[df_merged['color_group'] == color]
            if group_df.empty:
                continue

            st.markdown(f"### {color_names[color]} ({len(group_df)} cards)")

            cols = st.columns(6)
            for i, (_, row) in enumerate(group_df.iterrows()):
                img_url = row.get('image_url')
                name = row.get('name', 'Unknown')
                count = row.get('count', 1)
                label = f"{name} x{count}" if count > 1 else name

                if isinstance(img_url, str) and img_url.startswith("http"):
                    with cols[i % 6]:
                        st.image(
                            img_url,
                            caption=label,
                            use_container_width=True)






# Step 1: Recommend best color pairs
    df_merged['GIH WR'] = (
        df_merged['GIH WR']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.strip()
    )
    df_merged['GIH WR'] = pd.to_numeric(df_merged['GIH WR'], errors='coerce')

    top_pairs = suggest_color_pairs(df_merged)[:3]  # Top 3 recommendations

    # Step 2: Show decks for each pair
    for i, (pair, count, avg_wr, _) in enumerate(top_pairs):
        st.markdown(f"## 🧩 Recommended Deck {i+1}: {pair} ({count} cards, Avg WR {avg_wr:.2f})")

        main_deck, _, _ = build_deck(df_merged, color_pair=pair)


        st.write(f"✅ Built main deck with {len(main_deck)} cards")  # Debug

        with st.expander("Main Deck", expanded=True):
            if not main_deck.empty:
                st.dataframe(main_deck[['name', 'type_line', 'mana_cost', 'GIH WR', 'score']])
            else:
                st.warning("⚠️ Main deck is empty.")






