from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# used in my local development workflow
# after I sync media/db from the live site, I reset everyone's passwords
class Command(BaseCommand):
    help = 'reset all user passwords to "password"'

    def handle(self, *args, **options):
        for user in User.objects.all():
            user.set_password("password")
            user.save()
            self.stdout.write(
                self.style.SUCCESS('reset password for %s' % user.username)
            )
