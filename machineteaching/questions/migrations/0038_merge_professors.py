from django.conf import settings
from django.db import migrations, models


def merge_professor(apps, schema_editor):
    UserProfile = apps.get_model("questions", "UserProfile")
    Professor = apps.get_model("questions", "Professor")
    for obj_professor in Professor.objects.all():
        first_prof = Professor.objects.filter(user=obj_professor.user).order_by('pk')[0]
        all_users = UserProfile.objects.filter(professor__user=obj_professor.user)
        for u in all_users:
            u.professor = first_prof
            u.save()

def remove_professor(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0037_auto_20190808_1342'),
    ]

    operations = [
        migrations.RunPython(merge_professor, remove_professor),
    ]


