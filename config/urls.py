from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Our Kidney Story API",
        default_version='v1',
        description="API for Our Kidney Story platform",
        terms_of_service="https://www.ourkidneystory.com/terms/",
        contact=openapi.Contact(email="contact@ourkidneystory.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/stories/', include('stories.urls')),
    path('api/blogs/', include('blogs.urls')),
    path('api/forums/', include('forums.urls')),
    path('api/centers/', include('centers.urls')),
    path('api/products/', include('products.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/', include('core.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)