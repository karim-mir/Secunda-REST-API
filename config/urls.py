from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger документация
schema_view = get_schema_view(
    openapi.Info(
        title="Organization Catalog API",
        default_version='v1',
        description="API для справочника Организаций, Зданий, Деятельности",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def api_root(request):
    return JsonResponse({
        'message': 'Organization Catalog API',
        'endpoints': {
            'organizations': '/api/organizations/',
            'buildings': '/api/buildings/',
            'activities': '/api/activities/',
            'admin': '/admin/',
            'swagger_docs': '/swagger/',
            'redoc_docs': '/redoc/'
        },
        'instructions': 'Use ?api_key=test123 for authentication'
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("catalog.urls")),

    # Документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Корневой URL
    path('', api_root, name='api-root'),
]
