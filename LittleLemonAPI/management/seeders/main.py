from django.db import transaction

from .categories import seed_categories
from .groups import seed_groups
from .menu_items import seed_menu_items
from .users import DEFAULT_PASSWORD, seed_users


@transaction.atomic
def run_seed():
    """Ejecuta todos los seeds en el orden requerido."""
    groups = seed_groups()
    _, tokens = seed_users(groups)
    categories = seed_categories()
    seed_menu_items(categories)

    return {
        "password": DEFAULT_PASSWORD,
        "tokens": tokens,
    }

