from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Building, Activity, Organization


class ModelTests(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        self.building = Building.objects.create(
            address='г. Москва, ул. Тестовая 1',
            latitude=55.7558,
            longitude=37.6173
        )

        self.parent_activity = Activity.objects.create(name='Еда')
        self.child_activity = Activity.objects.create(
            name='Мясная продукция',
            parent=self.parent_activity
        )

        self.organization = Organization.objects.create(
            name='Тестовая организация',
            phone_numbers=['1-111-111', '2-222-222'],
            building=self.building
        )
        self.organization.activities.set([self.parent_activity, self.child_activity])

    def test_building_creation(self):
        """Тест создания здания"""
        self.assertEqual(self.building.address, 'г. Москва, ул. Тестовая 1')
        self.assertEqual(self.building.latitude, 55.7558)

    def test_activity_hierarchy(self):
        """Тест иерархии деятельностей"""
        self.assertEqual(self.child_activity.parent, self.parent_activity)
        self.assertEqual(self.child_activity.level, 2)
        self.assertIn(self.child_activity, self.parent_activity.children.all())

    def test_organization_relationships(self):
        """Тест связей организации"""
        self.assertEqual(self.organization.building, self.building)
        self.assertEqual(self.organization.activities.count(), 2)
        self.assertIn(self.parent_activity, self.organization.activities.all())


class APITests(APITestCase):
    def setUp(self):
        self.building = Building.objects.create(
            address='г. Москва, ул. API Тест 1',
            latitude=55.7558,
            longitude=37.6173
        )

        self.parent_activity = Activity.objects.create(name='Еда')
        self.child_activity = Activity.objects.create(
            name='Молочная продукция',
            parent=self.parent_activity
        )

        self.organization = Organization.objects.create(
            name='API Тест Организация',
            phone_numbers=['9-999-999'],
            building=self.building
        )
        self.organization.activities.set([self.child_activity])

        self.valid_api_key = 'test123'
        self.invalid_api_key = 'wrong_key'

    def test_organizations_list_with_valid_api_key(self):
        """Тест списка организаций с валидным API ключом"""
        url = reverse('organization-list')
        response = self.client.get(f'{url}?api_key={self.valid_api_key}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Обработка как пагинированного, так и непогинированного ответа
        if 'results' in response.data:
            # Пагинированный ответ (в продакшене)
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['name'], 'API Тест Организация')
        else:
            # Непагинированный ответ (в тестах)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['name'], 'API Тест Организация')

    def test_organizations_list_without_api_key(self):
        """Тест списка организаций без API ключа - должен быть запрещен"""
        url = reverse('organization-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizations_by_building(self):
        """Тест поиска организаций по зданию"""
        url = reverse('organization-by-building')
        response = self.client.get(
            f'{url}?building_id={self.building.id}&api_key={self.valid_api_key}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Если ответ пагинированный, берем results
        if isinstance(data, dict) and 'results' in data:
            data = data['results']

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'API Тест Организация')

    def test_organizations_by_activity(self):
        """Тест поиска организаций по деятельности (с иерархией)"""
        url = reverse('organization-by-activity')
        response = self.client.get(
            f'{url}?activity_id={self.parent_activity.id}&api_key={self.valid_api_key}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должна найти организацию с дочерней деятельностью
        self.assertEqual(len(response.data), 1)

    def test_organizations_search_by_name(self):
        """Тест поиска организаций по названию"""
        url = reverse('organization-search')
        response = self.client.get(
            f'{url}?name=API&api_key={self.valid_api_key}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_nearby_organizations(self):
        """Тест поиска организаций в радиусе"""
        url = reverse('organization-nearby')
        response = self.client.get(
            f'{url}?lat=55.7558&lon=37.6173&radius_km=1&api_key={self.valid_api_key}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('organizations', response.data)

    def test_activity_level_validation(self):
        """Тест валидации уровня вложенности деятельности"""
        # Создаем деятельность 3 уровня
        level3_activity = Activity.objects.create(
            name='Говядина',
            parent=self.child_activity  # child_activity уже 2 уровень
        )
        self.assertEqual(level3_activity.level, 3)

        # Попытка создать деятельность 4 уровня должна вызвать ошибку
        with self.assertRaises(ValueError):
            Activity.objects.create(
                name='Стейки',
                parent=level3_activity
            )
