from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


DEFAULT_PASSWORD = "mypassword123"
USERS = (
    {
        "username": "user1",
        "first_name": "Emily",
        "last_name": "Carter",
        "email": "user1@mail.com",
    },
    {
        "username": "user2",
        "first_name": "James",
        "last_name": "Anderson",
        "email": "user2@mail.com",
    },
    {
        "username": "user3",
        "first_name": "Olivia",
        "last_name": "Bennett",
        "email": "user3@mail.com",
    },
    {
        "username": "user4",
        "first_name": "Daniel",
        "last_name": "Wilson",
        "email": "user4@mail.com",
    },
    {
        "username": "user5",
        "first_name": "Sophie",
        "last_name": "Mitchell",
        "email": "user5@mail.com",
    },
    {
        "username": "user6",
        "first_name": "Henry",
        "last_name": "Thompson",
        "email": "user6@mail.com",
    },
)


def seed_users(groups):
    """Crea usuarios, asigna sus grupos y genera sus tokens."""
    users = {}
    for user_data in USERS:
        username = user_data["username"]
        user, _ = User.objects.get_or_create(username=username)
        user.set_password(DEFAULT_PASSWORD)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.is_staff = username == "user1"
        user.is_superuser = username == "user1"
        user.save(update_fields=[
            "password",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
        ])
        users[username] = user

    users["user1"].groups.set([groups["Manager"]])
    for username in ("user2", "user3", "user4"):
        users[username].groups.set([groups["Delivery crew"]])
    for username in ("user5", "user6"):
        users[username].groups.clear()

    tokens = {
        username: Token.objects.get_or_create(user=user)[0]
        for username, user in users.items()
    }
    return users, tokens
