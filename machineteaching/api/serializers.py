from rest_framework import serializers
from questions.models import DropoutRisk
from django.contrib.auth.models import User


class DropoutRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropoutRisk

        #Django Rest Framework shortcut so that it won't be necessary to write down all fields
        fields =  "__all__"   

    