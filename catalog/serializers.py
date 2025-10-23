from rest_framework import serializers
from .models import Organization, Building, Activity

class ActivitySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'name', 'parent', 'level', 'children']

    def get_children(self, obj):
        """Рекурсивно получаем детей, но только до 3 уровня"""
        if obj.level < 3:  # Ограничение вложенности как в ТЗ
            return ActivitySerializer(obj.children.all(), many=True).data
        return []

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'address', 'latitude', 'longitude']

class OrganizationSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'phone_numbers', 'building', 'activities']
