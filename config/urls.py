from django.urls import path

from careplans import views

urlpatterns = [
    path("", views.order_form, name="order_form"),
    path("download/<int:order_id>/", views.download_care_plan, name="download_care_plan"),
]
