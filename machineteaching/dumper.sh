echo "Dumping data"
$DJANGO_ENV $MT_FOLDER/machine-teaching/machineteaching/manage.py dumpdata --exclude=auth.user --exclude=questions.userprofile --indent=2 > django-data.json
mv django-data.json MachineTeaching/machine-teaching/machineteaching/django-dumpdata


#mkdir (criar pasta se n existir )
#ver se cria corretamente e se consegue  mover -> WORKING


