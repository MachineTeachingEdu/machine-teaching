from rest_framework import serializers
from questions.models import Recommendations


class RecommendationSerializer(serializers.Serializer):
    class Meta:
        model = Recommendations
        fields = ['user', 'problem', 'timestamp']

    def create(self, validated_data):
        return Recommendations.objects.create(**validated_data)