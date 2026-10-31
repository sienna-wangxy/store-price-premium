"""
clean_data.py
Clean the raw store price data and make a "product x store" price table.

Run from the project folder:
    python src/clean_data.py

Input:  data/raw/raw_prices.xlsx
Output: data/clean/prices_long.csv   (one row = one product at one store)
        data/clean/price_table.xlsx  (rows = products, columns = stores)
"""

from pathlib import Path

import pandas as pd

RAW_FILE = "data/raw/raw_prices.xlsx"
GROUND_TRUTH_FILES = ["data/raw/ground_truth.xlsx", "data/raw/ground_truth.csv"]
LONG_FILE = "data/clean/prices_long.csv"
TABLE_FILE = "data/clean/price_table.xlsx"

# ---------------------------------------------------------------
# Settings you can edit
# ---------------------------------------------------------------

# Clean store names
STORE_NAMES = {
    "durham coop": "Durham Co-op",
    "gazelle": "Gazelle",
    "bulldega": "Bulldega",
    "whole foods durham": "Whole Foods",
    "food lion": "Food Lion",
}

# Store type (please check this grouping is right!)
STORE_TYPES = {
    "Food Lion": "chain",
    "Whole Foods": "chain",
    "Durham Co-op": "co-op",
    "Bulldega": "small store",
    "Gazelle": "small store",
}

# Same brand written in different ways
BRAND_NAMES = {
    "rxbar": "RXBAR",
    "rx bar": "RXBAR",
}

# Product category, decided by brand
CATEGORIES = {
    "RXBAR": "snack bar",
    "Big Spoon": "snack bar",
    "Luna": "snack bar",
    "Kind": "snack bar",
    "Hu chocolate": "snack bar",
    "Kettle brand": "snack",
    "Pisgah": "beer",
    "Ponysaurus": "beer",
    "Sierra Nevada": "beer",
    "Blue Ribbon": "beer",
    "Budweiser": "beer",
    "Organic Valley": "dairy",
    "Annie's": "pantry",
    "Jovial": "pantry",
    "Rummo": "pantry",
}

# Words that really describe a shelf position
SHELF_WORDS = ["top", "middle", "bottom", "mid to top", "mid to bottom",
               "middle to bottom", "middle to top", "middle to too"]


# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def to_number(value):
    """Turn a cell into a number. Return None if it is not a number."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_sale_price(value):
    """
    Read the 'Discount' column.
    'N' or empty -> no sale
    '2/3.00'     -> 3.00 / 2 = 1.50 each
    a number     -> that number
    """
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.upper() == "N":
        return None
    if "/" in text:                      # e.g. "2/3.00"
        count, total = text.split("/")
        return float(total) / float(count)
    return to_number(text)


def load_controls():
    """Load one ground-truth export and coalesce the two reference sources.

    Storefront takes precedence if both prices are supplied; the sources are
    alternatives, not two observations to average. Notes describe pack sizes
    but do not override the supplied per-good prices.
    """
    path = next((Path(p) for p in GROUND_TRUTH_FILES if Path(p).exists()), None)
    if path is None:
        raise FileNotFoundError("Expected ground_truth.xlsx or ground_truth.csv in data/raw")
    controls = pd.read_excel(path) if path.suffix == ".xlsx" else pd.read_csv(path)
    controls.columns = controls.columns.str.strip()
    required = ["Brand", "Good", "Price on storefront", "Amazon / Total Wine", "Notes"]
    missing = set(required) - set(controls.columns)
    if missing:
        raise ValueError(f"Missing ground-truth columns: {sorted(missing)}")
    controls = controls.dropna(subset=["Brand", "Good"]).copy()
    controls["brand"] = controls["Brand"].astype(str).str.strip()
    controls["brand"] = controls["brand"].map(lambda b: BRAND_NAMES.get(b.lower(), b))
    controls["product"] = controls["Good"].astype(str).str.strip()
    controls["item"] = controls["brand"] + " | " + controls["product"]
    controls["item_key"] = controls["item"].str.casefold()
    for source, target in [("Price on storefront", "storefront_price"),
                           ("Amazon / Total Wine", "amazon_total_wine_price")]:
        controls[target] = pd.to_numeric(controls[source], errors="raise")
        if (controls[target].dropna() <= 0).any():
            raise ValueError(f"Control prices must be positive: {source}")
    controls["control_price"] = controls["storefront_price"].combine_first(
        controls["amazon_total_wine_price"])
    controls["control_source"] = pd.Series(pd.NA, index=controls.index, dtype="string")
    controls.loc[controls["amazon_total_wine_price"].notna(), "control_source"] = "Amazon / Total Wine"
    controls.loc[controls["storefront_price"].notna(), "control_source"] = "storefront"
    controls["control_note"] = controls["Notes"]
    if controls["item_key"].duplicated().any():
        raise ValueError("Duplicate brand/product in ground truth; resolve before merging")
    print("Control file:", path)
    return controls[["item_key", "item", "brand", "product", "storefront_price",
                     "amazon_total_wine_price", "control_price", "control_source", "control_note"]]



# ---------------------------------------------------------------
# 1. Read raw data
# ---------------------------------------------------------------
raw = pd.read_excel(RAW_FILE)
raw.columns = ["brand", "product", "store", "price_raw", "discount_raw",
               "shelf_raw", "note1", "note2"]
print("Raw rows:", len(raw))
controls = load_controls()

# ---------------------------------------------------------------
# 2. Clean row by row
# ---------------------------------------------------------------
rows = []
for _, r in raw.iterrows():

    # skip rows with no brand or no product name
    if pd.isna(r["brand"]) or pd.isna(r["product"]):
        continue

    brand = str(r["brand"]).strip()
    brand = BRAND_NAMES.get(brand.lower(), brand)
    product = str(r["product"]).strip()
    store = STORE_NAMES.get(str(r["store"]).strip().lower(), str(r["store"]).strip())

    price = to_number(r["price_raw"])
    sale_price = parse_sale_price(r["discount_raw"])

    # Notes: anything that tells us the item was not exactly the same
    notes = []
    member_price = None
    shelf = None

    # The shelf column sometimes has other info in it
    if not pd.isna(r["shelf_raw"]):
        shelf_text = str(r["shelf_raw"]).strip().lower()
        if shelf_text in SHELF_WORDS:
            shelf = shelf_text
        elif "prime" in shelf_text:                  # e.g. "1.60 (prime)"
            member_price = to_number(shelf_text.split("(")[0])
        else:                                        # e.g. "Caramel almond"
            notes.append(str(r["shelf_raw"]).strip())

    # Extra note columns (e.g. "Diff flavor", "IPA", "6 pack")
    for col in ["note1", "note2"]:
        if not pd.isna(r[col]):
            notes.append(str(r[col]).strip())

    # Price written as text (e.g. "4.58 (11 cents / oz pack of 6 ...)")
    if price is None and not pd.isna(r["price_raw"]):
        notes.append("price note: " + str(r["price_raw"]).strip())

    rows.append({
        "item": brand + " | " + product,
        "brand": brand,
        "product": product,
        "category": CATEGORIES.get(brand, "other"),
        "store": store,
        "store_type": STORE_TYPES.get(store, "unknown"),
        "regular_price": price,
        "sale_price": sale_price,
        "member_price": member_price,
        "shelf": shelf,
        "substitute": len(notes) > 0,     # True = not the exact same item
        "note": "; ".join(notes),
    })

data = pd.DataFrame(rows)

# Same item + store written twice -> keep the first one
data = data.drop_duplicates(subset=["item", "store"], keep="first")

# Price actually paid (sale price if there is one, otherwise regular price)
data["paid_price"] = data["sale_price"].fillna(data["regular_price"])

# Was the item found? (has a price)
data["found"] = data["regular_price"].notna()

# 2b. Attach the per-good control without adding artificial store observations.
# Matching ignores case and outer whitespace, but preserves flavor/pack size.
data["item_key"] = data["item"].str.casefold()
data = data.merge(controls.drop(columns=["item", "brand", "product"]),
                  on="item_key", how="left", validate="many_to_one")
data = data.drop(columns="item_key")
# Products absent from ground truth remain in the data with a missing control.
data["has_control"] = data["control_price"].notna()
# Substitute observations are retained for review but excluded from comparisons.
comparable = data["has_control"] & ~data["substitute"]
data["regular_premium_pct"] = ((data["regular_price"] / data["control_price"] - 1) * 100).where(comparable)
data["paid_premium_pct"] = ((data["paid_price"] / data["control_price"] - 1) * 100).where(comparable)

# Allow the script to run before the output directories have been created.
for output in [LONG_FILE, TABLE_FILE]:
    Path(output).parent.mkdir(parents=True, exist_ok=True)

print("Rows matched to a control:", data["has_control"].sum())
print("Clean rows:", len(data))
print("Rows with a price:", data["found"].sum())
print("Rows marked as substitute:", data["substitute"].sum())

data.to_csv(LONG_FILE, index=False)
print("Saved", LONG_FILE)


# ---------------------------------------------------------------
# 3. Make the "product x store" tables
# ---------------------------------------------------------------
store_order = ["Bulldega", "Durham Co-op", "Food Lion", "Gazelle", "Whole Foods"]

# Only exact matches (substitutes removed) go into the main table
exact = data[data["found"] & ~data["substitute"]]

regular_table = exact.pivot_table(index=["category", "item"], columns="store",
                                  values="regular_price", aggfunc="first")
regular_table = regular_table.reindex(columns=store_order)

paid_table = exact.pivot_table(index=["category", "item"], columns="store",
                               values="paid_price", aggfunc="first")
paid_table = paid_table.reindex(columns=store_order)

# How many stores have each item
regular_table["n_stores"] = regular_table[store_order].notna().sum(axis=1)


# Include the same reference price alongside store prices in both tables.
control_by_item = data.drop_duplicates("item").set_index("item")["control_price"]
for table in [regular_table, paid_table]:
    table["control_price"] = table.index.get_level_values("item").map(control_by_item)


# List of substitutes so you can check them
subs = data[data["substitute"]][["item", "store", "regular_price", "note"]]

with pd.ExcelWriter(TABLE_FILE) as writer:
    regular_table.to_excel(writer, sheet_name="regular_price")
    paid_table.to_excel(writer, sheet_name="paid_price")
    subs.to_excel(writer, sheet_name="substitutes_removed", index=False)
    data.to_excel(writer, sheet_name="long_data", index=False)
    controls.drop(columns="item_key").to_excel(writer, sheet_name="control_data", index=False)

print("Saved", TABLE_FILE)
print()
print(regular_table)
