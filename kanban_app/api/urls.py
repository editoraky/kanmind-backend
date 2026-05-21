from django.urls import path

from kanban_app.api.views import (
    BoardListCreateView,
    BoardDetailView,
    TaskCreateView,
    TaskDetailView,
    AssignedTasksView,
    ReviewingTasksView,
)

urlpatterns = [
    path('boards/', BoardListCreateView.as_view()),
    path('boards/<int:pk>/', BoardDetailView.as_view()),
    path('tasks/', TaskCreateView.as_view()),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view()),
    path('tasks/reviewing/', ReviewingTasksView.as_view()),
    path('tasks/<int:pk>/', TaskDetailView.as_view()),
]