"""Cuisine vocabulary of the app.

`classify_name` is a port of `CuisineClassifier.cuisine(for:)` in RestaurantParser.swift. The app
runs it itself when the `cuisine` column is empty, so the pipeline only writes `cuisine` when the
name says nothing ("Outros") and the Overture/OSM category maps to one of the app's cuisines.
"""

from .common import words

OTHER = "Outros"

RULES = [
    ("Hamburgueria", ["burger", "burguer", "hamburg"]),
    ("Pizzaria", ["pizza", "pizzeria", "forneria"]),
    ("Japonesa", ["sushi", "japon", "temaki", "sukiya", "yakitori", "izakaya", "ramen", "lamen", "sashimi", "nikkei"]),
    ("Árabe", ["habib", "arab", "liban", "esfiha", "esfirra", "almanara", "shawarma", "=saj"]),
    ("Churrascaria e carnes", ["churrasc", "steak", "grill", "parrilla", "costela", "carnes", "espeto", "rodeio",
                               "fogo de chao", "argentin"]),
    ("Italiana", ["cantina", "trattoria", "osteria", "italia", "spoleto", "pasta", "massas", "piadina", "ristorante",
                  "risot"]),
    ("Frutos do mar", ["peixe", "frutos do mar", "pescad", "seafood", "coco bambu", "camarao", "ostra"]),
    ("Mexicana", ["mexic", "taco", "burrito"]),
    ("Peruana", ["peru", "cevich"]),
    ("Chinesa", ["china", "chines", "wok", "dim sum", "yakisoba"]),
    ("Coreana", ["corea", "korea"]),
    ("Tailandesa", ["thai", "tailand"]),
    ("Indiana", ["india"]),
    ("Portuguesa", ["portugu", "bacalhau"]),
    ("Francesa", ["bistro", "frances", "brasserie", "creperia", "crepe"]),
    ("Vegetariana", ["vegan", "vegetarian", "natural"]),
    ("Brasileira", ["mineir", "feijoada", "nordest", "baian", "caseir", "fogao", "brasileir", "comida"]),
    ("Doces e sorvetes", ["chocolate", "cacau", "doce", "sorvet", "gelat", "bacio", "acai", "brigadeir", "cupcake",
                          "donut", "confeit"]),
    ("Padaria e café", ["padaria", "panificadora", "pao de queijo", "paes", "=cafe", "coffee", "cafeteria"]),
    ("Lanches", ["mcdonald", "subway", "lanche", "pastel", "hot dog", "=dog", "kebab", "sanduich", "=fast"]),
    ("Bar e boteco", ["=bar", "boteco", "buteco", "=pub", "chope", "cervej", "=beer", "botequim"]),
]


def classify_name(name):
    tokens = words(name)
    phrase = " " + " ".join(tokens) + " "
    for cuisine, keywords in RULES:
        for keyword in keywords:
            if keyword.startswith("="):
                hit = keyword[1:] in tokens
            elif " " in keyword:
                hit = f" {keyword} " in phrase
            else:
                hit = any(t.startswith(keyword) for t in tokens)
            if hit:
                return cuisine
    return OTHER


# Overture `taxonomy.primary` -> app cuisine. Generic categories ("restaurant", "fast_food_restaurant")
# are left out on purpose: the app's name classifier does better than a generic label.
TAXONOMY = {
    "pizza_restaurant": "Pizzaria",
    "burger_restaurant": "Hamburgueria",
    "japanese_restaurant": "Japonesa", "sushi_restaurant": "Japonesa", "ramen_restaurant": "Japonesa",
    "arabian_restaurant": "Árabe", "middle_eastern_restaurant": "Árabe", "lebanese_restaurant": "Árabe",
    "syrian_restaurant": "Árabe", "armenian_restaurant": "Árabe", "turkish_restaurant": "Árabe",
    "persian_restaurant": "Árabe",
    "barbecue_restaurant": "Churrascaria e carnes", "steakhouse": "Churrascaria e carnes",
    "argentine_restaurant": "Churrascaria e carnes", "uruguayan_restaurant": "Churrascaria e carnes",
    "bar_and_grill_restaurant": "Churrascaria e carnes",
    "italian_restaurant": "Italiana",
    "seafood_restaurant": "Frutos do mar", "fish_and_chips_restaurant": "Frutos do mar",
    "mexican_restaurant": "Mexicana", "texmex_restaurant": "Mexicana", "taco_restaurant": "Mexicana",
    "peruvian_restaurant": "Peruana",
    "chinese_restaurant": "Chinesa",
    "korean_restaurant": "Coreana",
    "thai_restaurant": "Tailandesa",
    "indian_restaurant": "Indiana",
    "portuguese_restaurant": "Portuguesa",
    "french_restaurant": "Francesa", "bistro": "Francesa",
    "vegetarian_restaurant": "Vegetariana", "vegan_restaurant": "Vegetariana",
    "health_food_restaurant": "Vegetariana", "salad_bar": "Vegetariana",
    "brazilian_restaurant": "Brasileira", "buffet_restaurant": "Brasileira",
    "ice_cream_shop": "Doces e sorvetes", "gelato_shop": "Doces e sorvetes", "dessert_shop": "Doces e sorvetes",
    "candy_store": "Doces e sorvetes", "chocolatier": "Doces e sorvetes", "cupcake_shop": "Doces e sorvetes",
    "donut_shop": "Doces e sorvetes", "frozen_yogurt_shop": "Doces e sorvetes",
    "bakery": "Padaria e café", "cafe": "Padaria e café", "coffee_shop": "Padaria e café",
    "tea_room": "Padaria e café", "cafeteria": "Padaria e café",
    "sandwich_shop": "Lanches", "hot_dog_restaurant": "Lanches", "diner": "Lanches",
    "doner_kebab_restaurant": "Lanches",
    "bar": "Bar e boteco", "pub": "Bar e boteco", "beer_bar": "Bar e boteco", "gastropub": "Bar e boteco",
    "beer_garden": "Bar e boteco", "sports_bar": "Bar e boteco", "wine_bar": "Bar e boteco",
    "cocktail_bar": "Bar e boteco", "irish_pub": "Bar e boteco", "dive_bar": "Bar e boteco",
}


def cuisine_column(name, taxonomy_primary):
    """Value for the `cuisine` column: empty when the app's own classifier already finds a cuisine."""
    if classify_name(name) != OTHER:
        return ""
    return TAXONOMY.get((taxonomy_primary or "").strip(), "")
