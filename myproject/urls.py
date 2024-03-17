from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("accounts/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("labs/", include("labs.urls", namespace="labs")),
    path("", include("core.urls", namespace="core")),
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#  <url_name>
# redirect("create-test")
# {% url 'create_test' %}
