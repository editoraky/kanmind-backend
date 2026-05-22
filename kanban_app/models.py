"""Database models for the Kanban domain: boards, tasks and comments."""

from django.db import models
from django.conf import settings


class Board(models.Model):
    """A Kanban board owned by one user and shared with optional members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_boards',)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_boards',)

    def __str__(self):
        """Return the board title for human-readable representations."""
        return self.title

class Task(models.Model):
    """A work item on a board with status, priority and optional assignees."""

    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to-do',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
    )
    due_date = models.DateField(null=True, blank=True)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review_tasks',
    )

    def __str__(self):
        """Return the task title for human-readable representations."""
        return self.title

class Comment(models.Model):
    """A user-authored comment attached to a single task."""

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_comments')

    class Meta:
        """Order comments chronologically by creation time."""

        ordering = ['created_at']

    def __str__(self):
        """Return a short author/content preview for admin and debugging."""
        return f'{self.author}: {self.content[:30]}'