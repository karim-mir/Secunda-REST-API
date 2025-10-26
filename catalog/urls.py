from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"organizations", views.OrganizationViewSet)
router.register(r"buildings", views.BuildingViewSet)
router.register(r"activities", views.ActivityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
