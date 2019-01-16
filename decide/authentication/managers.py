from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, **extra_fields):
        if not email:
            raise ValueError('The given email must be set, or published if you are trying to login with GitHub')
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        is_staff = False
        return self._create_user(email, password, is_staff, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        is_staff = True

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, is_staff, **extra_fields)