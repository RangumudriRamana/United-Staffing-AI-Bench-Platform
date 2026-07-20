from faker import Faker
from app.models.user import User
from app.auth.enums import Role

fake = Faker()

class UserFactory:
    @staticmethod
    def build(role: Role = Role.BENCH_SALES_RECRUITER, is_active: bool = True, **kwargs) -> User:
        """
        Builds an unpersisted transient User instance with realistic fake defaults.
        """
        defaults = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "hashed_password": "super-secure-hashed-dummy-string",
            "role": role,
            "is_active": is_active,
        }
        # Allow custom developer overrides to overwrite defaults smoothly
        defaults.update(kwargs)
        return User(**defaults)