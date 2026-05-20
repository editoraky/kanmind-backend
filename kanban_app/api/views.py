from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from kanban_app.models import Board
from kanban_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
)
from kanban_app.api.permissions import IsBoardOwnerOrMember


class BoardListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(RetrieveUpdateAPIView):
    http_method_names = ['get', 'patch', 'head', 'options']
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer