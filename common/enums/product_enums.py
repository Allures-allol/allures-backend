from enum import Enum

class ProductCategory(str, Enum):
    electronics = "electronics"
    bags = "bags"
    fashion = "fashion"
    personal_care = "personal_care"
    toys = "toys"
    home = "home"
    food = "food"
    outdoor = "outdoor"
    military = "military"
    automotive = "automotive"
    medical = "medical"
    office = "office"
    sports = "sports"
    art = "art"
    pets = "pets"
    diy = "diy"
    books = "books"
    beauty = "beauty"
    gadgets = "gadgets"
    bag = "bag"
    shoes = "shoes"
    outerwear = "outerwear"
    accessory = "accessory"


class ProductStatus(str, Enum):
    active = "active"
    inactive = "inactive"

