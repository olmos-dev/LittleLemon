from datetime import date, timedelta
from decimal import Decimal
from random import Random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from LittleLemonAPI.models import Cart, Category, MenuItem, Order, OrderItem


CATEGORIES = (
    ("Entradas", "entradas"), ("Ensaladas", "ensaladas"),
    ("Sopas", "sopas"), ("Pastas", "pastas"),
    ("Pizzas", "pizzas"), ("Carnes", "carnes"),
    ("Pescados", "pescados"), ("Vegetarianos", "vegetarianos"),
    ("Postres", "postres"), ("Bebidas", "bebidas"),
)

MENU_ITEM_NAMES = (
    "Bruschetta de tomate", "Hummus con pan pita", "Croquetas de jamon", "Calamares fritos", "Nachos con guacamole", "Alitas buffalo", "Queso fundido", "Champinones al ajillo", "Empanadas de carne", "Tabla de quesos",
    "Ensalada Cesar", "Ensalada griega", "Ensalada caprese", "Ensalada de quinoa", "Ensalada Waldorf", "Ensalada de atun", "Ensalada mediterranea", "Ensalada de espinaca", "Ensalada de pollo", "Ensalada de aguacate",
    "Sopa de tomate", "Sopa de cebolla", "Crema de champinones", "Sopa minestrone", "Crema de calabaza", "Sopa de tortilla", "Caldo de pollo", "Sopa de mariscos", "Crema de brocoli", "Sopa de lentejas",
    "Espagueti carbonara", "Lasana bolonesa", "Fettuccine Alfredo", "Penne arrabbiata", "Ravioles de queso", "Canelones de espinaca", "Linguini con camarones", "Macarrones con queso", "Pasta primavera", "Tortellini al pesto",
    "Pizza Margarita", "Pizza Pepperoni", "Pizza Cuatro Quesos", "Pizza Hawaiana", "Pizza Vegetariana", "Pizza Prosciutto", "Pizza de champinones", "Pizza BBQ", "Pizza Napolitana", "Pizza Mexicana",
    "Pollo Cordon Bleu", "Filete mignon", "Costillas BBQ", "Pollo a la parrilla", "Milanesa de res", "Chuletas de cerdo", "Hamburguesa clasica", "Carne asada", "Pollo al limon", "Estofado de res",
    "Salmon al limon", "Filete de atun", "Pescado empanizado", "Camarones al ajillo", "Pulpo a la gallega", "Tilapia a la plancha", "Tacos de pescado", "Ceviche de pescado", "Paella de mariscos", "Trucha con almendras",
    "Berenjena parmesana", "Falafel con tahini", "Tacos de champinones", "Curry de garbanzos", "Hamburguesa vegetariana", "Tofu teriyaki", "Risotto de hongos", "Chiles rellenos de queso", "Quiche de espinaca", "Verduras a la parrilla",
    "Helado de vainilla", "Pastel de chocolate", "Tiramisu", "Cheesecake de fresa", "Brownie con helado", "Panna cotta", "Creme brulee", "Flan napolitano", "Tarta de manzana", "Mousse de chocolate",
    "Limonada natural", "Agua de horchata", "Te helado de durazno", "Cafe americano", "Chocolate caliente", "Jugo de naranja", "Batido de fresa", "Agua mineral", "Capuchino", "Malteada de chocolate",
)

REQUIRED_USERS = {"user1", "user2", "user3", "user4", "user5", "user6"}
DELIVERY_USERNAMES = ("user2", "user3", "user4")
CLIENT_USERNAMES = ("user5", "user6")


class Command(BaseCommand):
    help = (
        "Recrea 10 categorias, 100 platillos y 100 pedidos usando solamente "
        "los usuarios existentes; el carrito queda vacio."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        users = User.objects.in_bulk(REQUIRED_USERS, field_name="username")
        missing_users = sorted(REQUIRED_USERS - users.keys())
        if missing_users:
            raise CommandError(
                "Faltan usuarios requeridos: " + ", ".join(missing_users)
            )

        delivery_crew = [users[name] for name in DELIVERY_USERNAMES]
        clients = [users[name] for name in CLIENT_USERNAMES]

        invalid_delivery = [
            user.username for user in delivery_crew
            if not user.groups.filter(name="Delivery crew").exists()
        ]
        if invalid_delivery:
            raise CommandError(
                "No pertenecen a Delivery crew: " + ", ".join(invalid_delivery)
            )
        invalid_clients = [user.username for user in clients if user.groups.exists()]
        if invalid_clients:
            raise CommandError(
                "Deben ser clientes sin grupo: " + ", ".join(invalid_clients)
            )

        # Se reconstruyen los datos comerciales, pero nunca los usuarios.
        Cart.objects.all().delete()
        Order.objects.all().delete()
        MenuItem.objects.all().delete()
        Category.objects.all().delete()

        categories = [
            Category.objects.create(title=title, slug=slug)
            for title, slug in CATEGORIES
        ]
        menu_items = self._create_menu_items(categories)
        self._create_orders(Random(42), clients, delivery_crew, menu_items)

        self.stdout.write(self.style.SUCCESS(
            "Base poblada: 10 categorias, 100 menu items y 100 pedidos."
        ))
        self.stdout.write(
            "Usuarios conservados; cada pedido tiene de 2 a 5 items y Cart esta vacio."
        )

    def _create_menu_items(self, categories):
        menu_items = []
        for index, title in enumerate(MENU_ITEM_NAMES):
            price = Decimal(5 + (index % 36)) + Decimal(index % 4) * Decimal("0.25")
            menu_items.append(MenuItem(
                title=title,
                price=price,
                featured=(index + 1) % 8 != 0,
                category=categories[index // 10],
            ))
        return MenuItem.objects.bulk_create(menu_items)

    def _create_orders(self, random, clients, delivery_crew, menu_items):
        today = date.today()

        for number in range(1, 101):
            selected_items = random.sample(menu_items, random.randint(2, 5))
            item_values = []
            total = Decimal("0.00")

            for menu_item in selected_items:
                quantity = random.randint(1, 4)
                price = menu_item.price * quantity
                total += price
                item_values.append((menu_item, quantity, price))

            order = Order.objects.create(
                user=clients[(number - 1) % len(clients)],
                delivery_crew=delivery_crew[(number - 1) % len(delivery_crew)],
                status=number % 3 == 0,
                total=total,
                date=today - timedelta(days=(number - 1) % 30),
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    menuitem=menu_item,
                    quantity=quantity,
                    unit_price=menu_item.price,
                    price=price,
                )
                for menu_item, quantity, price in item_values
            ])
