from decimal import Decimal

from LittleLemonAPI.models import MenuItem


MENU_ITEMS = (
    ("Bruschetta", "6.50", False, "entradas"),
    ("Hummus con pan pita", "7.00", True, "entradas"),
    ("Ensalada griega", "8.50", False, "entradas"),
    ("Calamares fritos", "9.75", True, "entradas"),
    ("Pasta carbonara", "14.50", True, "platos-principales"),
    ("Pizza margarita", "12.00", True, "platos-principales"),
    ("Pollo a la parrilla", "16.25", True, "platos-principales"),
    ("Salmon al limon", "19.50", True, "platos-principales"),
    ("Tiramisu", "7.50", True, "postres"),
    ("Cheesecake", "7.00", True, "postres"),
    ("Brownie con helado", "6.75", True, "postres"),
    ("Panna cotta", "7.25", True, "postres"),
)


def seed_menu_items(categories):
    """Crea o actualiza los doce alimentos."""
    for title, price, featured, category_slug in MENU_ITEMS:
        MenuItem.objects.update_or_create(
            title=title,
            defaults={
                "price": Decimal(price),
                "featured": featured,
                "category": categories[category_slug],
            },
        )
