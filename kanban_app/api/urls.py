from django.urls import path

from kanban_app.api.views import BoardListCreateView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view()),
]