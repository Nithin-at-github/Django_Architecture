from django.apps import AppConfig


class AppBaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_training.app_base"
    verbose_name = "Application Base Architecture"
