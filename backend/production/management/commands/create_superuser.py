from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a superuser for Railway deployment'

    def handle(self, *args, **options):
        username = 'railwayde'
        email = 'admin@admin.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists!'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))

