import math
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from django.db.models import Q

from .models import Organization, Building, Activity
from .serializers import *


@api_view(['GET'])
def api_root(request):
    """Корневой URL с информацией об API"""
    return Response({
        'message': 'Organization Catalog API',
        'endpoints': {
            'organizations': '/api/organizations/',
            'buildings': '/api/buildings/',
            'activities': '/api/activities/',
            'documentation': '/api/'
        }
    })


class APIKeyPermission(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем доступ если API ключ правильный ИЛИ если его нет вообще
        api_key = request.query_params.get('api_key')

        # Если API ключ передан - проверяем его
        if api_key is not None:
            return api_key == 'test123'

        # Если API ключ не передан - запрещаем доступ
        return False


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Расчет расстояния между двумя точками в км
    """
    R = 6371  # Радиус Земли в км

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related('building').prefetch_related('activities').order_by('id')
    serializer_class = OrganizationSerializer
    permission_classes = [APIKeyPermission]

    @action(detail=False, methods=['get'])
    def by_building(self, request):
        """Список организаций в конкретном здании"""
        building_id = request.query_params.get('building_id')
        if not building_id:
            return Response({"error": "building_id parameter is required"}, status=400)

        organizations = self.queryset.filter(building_id=building_id)
        serializer = self.get_serializer(organizations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_activity(self, request):
        """Список организаций по виду деятельности (включая дочерние)"""
        activity_id = request.query_params.get('activity_id')
        if not activity_id:
            return Response({"error": "activity_id parameter is required"}, status=400)

        def get_child_activity_ids(parent_id):
            activities = Activity.objects.filter(parent_id=parent_id)
            ids = [parent_id]
            for activity in activities:
                ids.extend(get_child_activity_ids(activity.id))
            return ids

        activity_ids = get_child_activity_ids(int(activity_id))
        organizations = self.queryset.filter(activities__id__in=activity_ids).distinct()
        serializer = self.get_serializer(organizations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Организации в радиусе от указанной точки"""
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius_km = float(request.query_params.get('radius_km', 1.0))
        except (TypeError, ValueError):
            return Response({"error": "Invalid parameters"}, status=400)

        organizations = []
        for org in self.queryset:
            building = org.building
            distance = calculate_distance_km(lat, lon, building.latitude, building.longitude)
            if distance <= radius_km:
                organizations.append(org)

        serializer = self.get_serializer(organizations, many=True)
        return Response({
            'organizations': serializer.data,
            'search_center': {'lat': lat, 'lon': lon},
            'radius_km': radius_km
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск организаций по названию"""
        name = request.query_params.get('name', '')
        if not name:
            return Response({"error": "name parameter is required"}, status=400)

        organizations = self.queryset.filter(name__icontains=name)
        serializer = self.get_serializer(organizations, many=True)
        return Response(serializer.data)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [APIKeyPermission]


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [APIKeyPermission]
