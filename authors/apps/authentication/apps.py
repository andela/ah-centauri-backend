from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'authors.apps.authentication'

    def ready(self):
        import authors.apps.authentication.signals
