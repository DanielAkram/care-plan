from django.urls import path

from careplans import views

urlpatterns = [
    path("", views.order_form, name="order_form"),
    path("download/<int:order_id>/", views.download_care_plan, name="download_care_plan"),
    path("api/orders/<int:order_id>/", views.get_order, name="get_order"),
]
