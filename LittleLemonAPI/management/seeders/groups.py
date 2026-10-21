from django.contrib.auth.models import Group


GROUP_NAMES = ("Manager", "Delivery crew")


def seed_groups():
    """Crea los grupos y los devuelve indexados por nombre."""
    return {
        name: Group.objects.get_or_create(name=name)[0]
        for name in GROUP_NAMES
    }

