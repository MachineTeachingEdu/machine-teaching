echo "Dumping data"
source $PWD/.env
$DJANGO_ENV $MT_FOLDER/machine-teaching/machineteaching/manage.py dumpdata --exclude=auth.user --exclude=questions.userprofile --indent=2 > django-data.json
mv django-data.json $MT_FOLDER/machine-teaching/machineteaching/django-dumpdata




