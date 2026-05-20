from django.urls import path

from kanban_app.api.views import (
    BoardListCreateView,
    BoardDetailView,
    TaskCreateView,
)

urlpatterns = [
    path('boards/', BoardListCreateView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view()),
    path('tasks/', TaskCreateView.as_view()),
]