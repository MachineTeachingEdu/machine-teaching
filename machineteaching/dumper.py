#this script makes a monthly dump of the django data without personal info models
import os 
import datetime

date = datetime.datetime.now()


def dumping():
    print("Dumping data at", date)
    cmd = "/usr/bin/python3 /home/renan/MachineTeaching/machine-teaching/machineteaching/manage.py dumpdata --exclude=auth.user --exclude=questions.userprofile --indent=2 > django_data.json"
    os.system(cmd)
    os.system("mv django_data.json django-dumpdata")

dumping()
