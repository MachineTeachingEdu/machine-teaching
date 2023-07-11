from django.conf import settings
from django.db import migrations, models


def delete_duplicate_professor(apps, schema_editor):
    Professor = apps.get_model("questions", "Professor")
    UserProfile = apps.get_model("questions", "UserProfile")
    real_prof = UserProfile.objects.all().values_list('professor', flat=True).distinct()
    Professor.objects.exclude(pk__in=real_prof).delete()

def remove_professor(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0040_userprofile_sequential'),
    ]

    operations = [
        migrations.RunPython(delete_duplicate_professor, remove_professor),
    ]


