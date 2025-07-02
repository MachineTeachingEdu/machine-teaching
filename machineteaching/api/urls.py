from .views import DropoutRiskViewSet, StudentViewRowAPIView
from rest_framework.routers import DefaultRouter
from django.urls import path 

router = DefaultRouter()
router.register(r'dropoutRisk', DropoutRiskViewSet)

urlpatterns = router.urls + [
    path('student-view/', StudentViewRowAPIView.as_view(), name='student-view'),
]