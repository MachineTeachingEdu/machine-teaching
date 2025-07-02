from rest_framework import viewsets
from questions import models
from .serializers  import DropoutRiskSerializer

class DropoutRiskViewSet(viewsets.ModelViewSet):
    queryset = models.DropoutRisk.objects.all()
    serializer_class = DropoutRiskSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class StudentViewRowAPIView(APIView):
    allowed_views = {
        'user_chapter_attempts': 'user_chapter_attempts',
        'user_chapter_success': 'user_chapter_success',
        'user_chapter_success_rate': 'user_chapter_success_rate',
        'user_chapter_submissions': 'user_chapter_submissions',
    }

    def get(self, request, format=None):
        student_id = request.query_params.get('student_id')
        view_key = request.query_params.get('view_name')

        if not student_id or not view_key:
            return Response({'error': 'Parâmetros student_id e view_name são obrigatórios.'},
                            status=status.HTTP_400_BAD_REQUEST)

        view_name = self.allowed_views.get(view_key)
        if not view_name:
            return Response({'error': f'view_name inválido. Use um destes: {list(self.allowed_views.keys())}'},
                            status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {view_name} WHERE user_id = %s", [student_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if rows else []

        if not rows:
            return Response({'error': 'Nenhum registro encontrado para esse student_id.'},
                            status=status.HTTP_404_NOT_FOUND)

        result_list = []
        for row in rows:
            # Para cada tupla (linha), criamos um dict com {coluna: valor}
            item = dict(zip(columns, row))
            result_list.append(item)

        return Response(result_list, status=status.HTTP_200_OK)


