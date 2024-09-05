from .views import DropoutRiskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'dropoutRisk', DropoutRiskViewSet)
urlpatterns = router.urls