from django.conf import settings
from django.db import migrations, models


def add_professor(apps, schema_editor):
    UserProfile = apps.get_model("questions", "UserProfile")
    User = apps.get_model("auth", "User")
    Professor = apps.get_model("questions", "Professor")
    for obj_userprofile in UserProfile.objects.all():
        user = User.objects.get_or_create(username=obj_userprofile.professor)
        prof = Professor.objects.create(user=user[0])
        obj_userprofile.professor2 = prof
        obj_userprofile.save()

def remove_professor(apps, schema_editor):
    Professor = apps.get_model("questions", "Professor")
    Professor.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0034_auto_20190808_1314'),
    ]

    operations = [
        migrations.RunPython(add_professor, remove_professor),
    ]


