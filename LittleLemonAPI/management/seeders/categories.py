from LittleLemonAPI.models import Category


CATEGORIES = (
    ("Entradas", "entradas"),
    ("Platos principales", "platos-principales"),
    ("Postres", "postres"),
)


def seed_categories():
    """Crea las categorias y las devuelve indexadas por slug."""
    categories = {}
    for title, slug in CATEGORIES:
        category, _ = Category.objects.update_or_create(
            slug=slug,
            defaults={"title": title},
        )
        categories[slug] = category
    return categories

