from django.core.management.base import BaseCommand
from catalog.models import Building, Activity, Organization
from django.contrib.auth import get_user_model
import json


class Command(BaseCommand):
    help = 'Fill database with test data for Organization Catalog'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        # Очищаем существующие данные
        # Organization.objects.all().delete()
        # Activity.objects.all().delete()
        # Building.objects.all().delete()

        # 1. Создаем здания
        buildings_data = [
            {
                'address': 'г. Москва, ул. Ленина 1, офис 3',
                'latitude': 55.7558,
                'longitude': 37.6173
            },
            {
                'address': 'г. Москва, ул. Тверская 10',
                'latitude': 55.7600,
                'longitude': 37.6100
            },
            {
                'address': 'г. Москва, ул. Арбат 25',
                'latitude': 55.7500,
                'longitude': 37.5900
            }
        ]

        buildings = []
        for building_data in buildings_data:
            building, created = Building.objects.get_or_create(
                address=building_data['address'],
                defaults=building_data
            )
            buildings.append(building)
            self.stdout.write(f'Building: {building.address}')

        # 2. Создаем древовидные деятельности
        activities_data = [
            {'name': 'Еда', 'parent': None},
            {'name': 'Мясная продукция', 'parent': 'Еда'},
            {'name': 'Молочная продукция', 'parent': 'Еда'},
            {'name': 'Автомобили', 'parent': None},
            {'name': 'Грузовые', 'parent': 'Автомобили'},
            {'name': 'Легковые', 'parent': 'Автомобили'},
            {'name': 'Запчасти', 'parent': 'Легковые'},
            {'name': 'Аксессуары', 'parent': 'Легковые'},
            {'name': 'IT услуги', 'parent': None},
            {'name': 'Разработка ПО', 'parent': 'IT услуги'},
            {'name': 'Тестирование', 'parent': 'IT услуги'},
        ]

        activities = {}
        for activity_data in activities_data:
            parent = None
            if activity_data['parent']:
                parent = activities[activity_data['parent']]

            activity, created = Activity.objects.get_or_create(
                name=activity_data['name'],
                parent=parent
            )
            activities[activity_data['name']] = activity
            self.stdout.write(f'Activity: {activity.name} (level {activity.level})')

        # 3. Создаем организации
        organizations_data = [
            {
                'name': 'ООО "Рога и Копыта"',
                'phone_numbers': ['2-222-222', '3-333-333'],
                'building': 'г. Москва, ул. Ленина 1, офис 3',
                'activities': ['Мясная продукция', 'Молочная продукция']
            },
            {
                'name': 'АвтоМир',
                'phone_numbers': ['8-923-666-13-13'],
                'building': 'г. Москва, ул. Тверская 10',
                'activities': ['Легковые', 'Запчасти', 'Аксессуары']
            },
            {
                'name': 'Грузовик Сервис',
                'phone_numbers': ['4-444-444', '5-555-555'],
                'building': 'г. Москва, ул. Арбат 25',
                'activities': ['Грузовые', 'Запчасти']
            },
            {
                'name': 'IT Solutions',
                'phone_numbers': ['6-666-666'],
                'building': 'г. Москва, ул. Ленина 1, офис 3',
                'activities': ['Разработка ПО', 'Тестирование']
            }
        ]

        for org_data in organizations_data:
            building = Building.objects.get(address=org_data['building'])
            activity_objs = [activities[name] for name in org_data['activities']]

            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults={
                    'phone_numbers': org_data['phone_numbers'],
                    'building': building
                }
            )
            org.activities.set(activity_objs)
            self.stdout.write(f'Organization: {org.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created test data!')
        )
        self.stdout.write(f'Buildings: {Building.objects.count()}')
        self.stdout.write(f'Activities: {Activity.objects.count()}')
        self.stdout.write(f'Organizations: {Organization.objects.count()}')
