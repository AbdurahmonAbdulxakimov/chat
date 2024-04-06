from django.urls import path


from users.api.views import UserViewSet

app_name = "users"
urlpatterns = [
    path("me/", view=UserViewSet.as_view(), name="me"),
]
