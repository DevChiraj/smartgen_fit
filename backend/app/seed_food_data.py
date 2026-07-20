"""Parses the Module 12 Kaggle nutrition dataset into rows for
sri_lankan_foods. Kept separate from seed.py's small hand-written
reference tables since this is a 119-row real dataset needing real
parsing, not a short literal list.

Source: Kaggle `nipunaudara/nutritional-facts-for-most-common-sri-lankan-foods`
(CC0-1.0), replacing the original 12-row manually-curated placeholder
per CLAUDE.md rule 6 ("try Kaggle first... manual data is a fallback").
The dataset has no category/fiber/vitamin/mineral columns - fiber_g,
vitamins, minerals, image_url are left null rather than invented, and
category is assigned via an explicit, auditable per-food mapping below
(deliberately not keyword heuristics - "Chocolate Marie biscuit" would
misfire on both "Chocolate" and "biscuit" keyword rules).
"""

import re
from pathlib import Path

import pandas as pd

from app.config import PROJECT_ROOT

FOOD_XLSX = Path(PROJECT_ROOT) / "datasets" / "sri_lankan_foods" / "SrilankanCommonFoods.xlsx"

# Every food name in the source dataset, mapped to one of these categories.
# Grain/Legume/Protein/Vegetable/Fruit/Condiment mirror the original
# Module 2 placeholder's categories; Dairy/Sweet/Snack/Beverage/
# "Nuts & Seeds"/"Fat & Oil" were added because the real dataset covers
# far more ground (bakery, biscuits, dried fish, dairy) than the 12-item
# placeholder did.
FOOD_CATEGORIES = {
    "White Rice": "Grain",
    "Brown Rice": "Grain",
    "Red Rice": "Grain",
    "White Bread": "Grain",
    "Pasta": "Grain",
    "Roast Paan": "Grain",
    "Thati Paan": "Grain",
    "Coconut Roti": "Grain",
    "White Noodles": "Grain",
    "Idiyappam": "Grain",
    "Hoppers": "Grain",
    "Kiribath": "Grain",
    "Lunu Miris": "Condiment",
    "Boiled Cowpea": "Legume",
    "Coconut Sambal": "Condiment",
    "Papadam": "Condiment",
    "Egg": "Protein",
    "Dhal Curry with coconut milk": "Legume",
    "Dhal Curry": "Legume",
    "Yellow Rice": "Grain",
    "Fried Halmesso": "Protein",
    "Fried Karawala": "Protein",
    "Kola Mallum": "Vegetable",
    "Cucumber Salad": "Vegetable",
    "Vegetable curry with coconut milk": "Vegetable",
    "Vegetable curry with coconut oil": "Vegetable",
    "Kiri Hodi": "Condiment",
    "Beetroot curry with coconut milk": "Vegetable",
    "Soya meat curry with coconut milk": "Legume",
    "Soya meat curry": "Legume",
    "Boiled Potatoes": "Vegetable",
    "Chicken Curry": "Protein",
    "Chicken Gravy": "Protein",
    "Vegetable Soup": "Vegetable",
    "Egg Yolk": "Protein",
    "Mango Chutney": "Condiment",
    "Mango Chutney with Sugar": "Condiment",
    "Boiled Jackfruit Seed": "Vegetable",
    "Boiled Chickpeas": "Legume",
    "Boiled Mung": "Legume",
    "Boiled Sweet Potato": "Vegetable",
    "Cucumber Flesh": "Vegetable",
    "Tomato sauce": "Condiment",
    "White sugar": "Condiment",
    "Coconut Milk 1st 2nd 3rd extractions": "Condiment",
    "Coconut Milk 1st 2nd extractions": "Condiment",
    "Coconut Milk 1st extraction": "Condiment",
    "Roast Peanut": "Nuts & Seeds",
    "Roast Green Pea": "Nuts & Seeds",
    "Roasted Gram": "Nuts & Seeds",
    "Orange": "Fruit",
    "Guava": "Fruit",
    "Kurumba": "Fruit",
    "Ambun Kesel": "Fruit",
    "Banana": "Fruit",
    "Ambul Kesel": "Fruit",
    "Cavendish Banana": "Fruit",
    "Raisins": "Fruit",
    "Jackfruit": "Fruit",
    "Avocado": "Fruit",
    "Watermelon": "Fruit",
    "Dodol": "Sweet",
    "Mun Kawum": "Sweet",
    "Aluwa": "Sweet",
    "Helapa": "Sweet",
    "Wandu": "Sweet",
    "Ada": "Sweet",
    "Samaposha Aggala": "Sweet",
    "Cream Bun": "Sweet",
    "Kibula Banis": "Sweet",
    "Saw Kanji": "Beverage",
    "Lavariya": "Sweet",
    "Vegetable Roll": "Snack",
    "Jam Paan": "Sweet",
    "Gal Banis": "Grain",
    "Coconut Cake": "Sweet",
    "Butter Cake": "Sweet",
    "Chocolate Cake": "Sweet",
    "Choco bar": "Sweet",
    "Dark chocolate": "Sweet",
    "Chocolate": "Sweet",
    "Fruit & Nut ice cream": "Sweet",
    "Chocolate ice cream": "Sweet",
    "Wonder choc ice cream": "Sweet",
    "Milk cream biscuit": "Snack",
    "Lemon puff": "Snack",
    "Marie biscuit": "Snack",
    "Chocolate Marie biscuit": "Snack",
    "Chocolate Cream Biscuit": "Snack",
    "Orange cream biscuit": "Snack",
    "Gold Marie biscuit": "Snack",
    "Cream cracker biscuit": "Snack",
    "Nice biscuit": "Snack",
    "Hawaiian cookie": "Snack",
    "Ginger Finger Biscuit": "Snack",
    "Custard cream biscuit": "Snack",
    "Batter Carol biscuit": "Snack",
    "Pani Murukku": "Snack",
    "Boondi": "Snack",
    "Jelly Jujub": "Sweet",
    "Garlic Murukku": "Snack",
    "Murukku": "Snack",
    "Thala Bola": "Sweet",
    "Yogurt": "Dairy",
    "Kotmale Vanilla milk": "Dairy",
    "Necto": "Beverage",
    "Quinoa": "Grain",
    "Oats": "Grain",
    "Chicken Breast": "Protein",
    "Salmon": "Protein",
    "Tuna": "Protein",
    "Whole Milk": "Dairy",
    "Skim Milk": "Dairy",
    "Greek Yogurt": "Dairy",
    "Apple": "Fruit",
    "Olive Oil": "Fat & Oil",
    "Almonds": "Nuts & Seeds",
    "Walnuts": "Nuts & Seeds",
    "Peanut Butter": "Nuts & Seeds",
}


def _parse_number(value: str) -> float:
    match = re.match(r"[\d.]+", str(value).strip())
    if match is None:
        raise ValueError(f"Could not parse a number from {value!r}")
    return float(match.group())


def load_food_records(path=FOOD_XLSX) -> list[dict]:
    df = pd.read_excel(path)
    records = []
    for row in df.to_dict(orient="records"):
        food_name = str(row["Food"]).strip()
        category = FOOD_CATEGORIES.get(food_name)
        if category is None:
            raise ValueError(f"No category mapped for {food_name!r} - add it to FOOD_CATEGORIES.")
        records.append(
            dict(
                food_name=food_name,
                category=category,
                serving_size=str(row["Quantity"]).strip(),
                calories=int(_parse_number(row["Calories (kcal)"])),
                carbs_g=_parse_number(row["Carbohydrate (g)"]),
                protein_g=_parse_number(row["Protein (g)"]),
                fat_g=_parse_number(row["Fat (g)"]),
            )
        )
    return records
