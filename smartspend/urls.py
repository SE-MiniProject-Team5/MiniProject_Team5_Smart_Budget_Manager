from django.contrib import admin
from django.urls import include, path
from . import views
urlpatterns = [
path("admin/", admin.site.urls),
path("", views.home, name="home"),
path("api/v1/health/", views.health, name="health"),
# Each app owns its own urls.py, so nobody needs to edit this file again.
path("api/v1/", include("accounts.urls")),
path("api/v1/", include("expenses.urls")),
path("api/v1/", include("budgets.urls")),
path("api/v1/", include("reports.urls")),
]
