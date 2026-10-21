from django.core.management.base import BaseCommand

from LittleLemonAPI.management.seeders.main import run_seed


class Command(BaseCommand):
    help = "Crea los grupos, usuarios, categorias y alimentos iniciales."

    def handle(self, *args, **options):
        result = run_seed()

        self.stdout.write(self.style.SUCCESS(
            "Seed completado: 2 grupos, 6 usuarios, 3 categorias y 12 alimentos."
        ))
        self.stdout.write(
            f"Password de los usuarios: {result['password']}"
        )
        for username, token in result["tokens"].items():
            self.stdout.write(f"Token de {username}: {token.key}")
