from rest_framework.routers import DefaultRouter
from django.urls import path,include


router = DefaultRouter()

from .views import ConversationViewSet
router.register("conversations", ConversationViewSet)
urlpatterns = [
    path('conversation/', include(router.urls)),
]