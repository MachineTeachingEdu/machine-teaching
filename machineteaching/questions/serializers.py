from rest_framework import serializers
from questions.models import Recommendations, Problem, Solution, TestCase
import json


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = ['user', 'problem', 'timestamp']

    def create(self, validated_data):
        return Recommendations.objects.create(**validated_data)


#Serializers usados pelo worker-node
class TestCaseSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    languages = serializers.StringRelatedField(many=True)  #Adicionando o relacionamento Many-to-Many
    
    class Meta:
        model = TestCase
        fields = ['content', 'languages']

    def get_content(self, obj):
        return json.loads(obj.content)   #Retornando o conteúdo do campo content em formato json


class SolutionSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()

    class Meta:
        model = Solution
        fields = ['content', 'header', 'language', 'return_type', 'ignore']


class ProblemSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True, source='testcase_set')
    solutions = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = ['id', 'content', 'test_cases', 'solutions']

    def get_solutions(self, obj):
        solutions = Solution.objects.filter(problem=obj, ignore=False)   #Retornando soluções de todas as linguagens
        return SolutionSerializer(solutions, many=True).data