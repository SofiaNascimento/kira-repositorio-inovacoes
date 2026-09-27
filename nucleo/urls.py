from django.urls import path

from nucleo.views import HomeInternaView

app_name = "nucleo"

urlpatterns = [
    path("", HomeInternaView.as_view(), name="home"),
]
