from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path,re_path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from django.urls import path,include


router = DefaultRouter()

router.register("messages", MessageViewSet)
router.register("conversations", ConversationViewSet)


urlpatterns = [
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('',home,name='home'),
    path('login/',LoginUserView.as_view(),name='login'),
    path('imagemessage/<conversation_name>/',PostImageMessageView.as_view(),name='imagemessage'),
    path('', include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
