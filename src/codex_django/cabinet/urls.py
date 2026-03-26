from django.urls import path

from .views import dashboard_view, site_settings_tab_view, site_settings_view

# No app_name here — the project's cabinet/urls.py owns the 'cabinet' namespace
# and includes these patterns via include("codex_django.cabinet.urls")

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("site/settings/", site_settings_view, name="site_settings"),
    path("site/settings/<str:tab>/", site_settings_tab_view, name="site_settings_tab"),
]
