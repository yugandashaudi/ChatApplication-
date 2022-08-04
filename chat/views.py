from django.forms import ImageField
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ImageMessageSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework.response import Response 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from .models import Conversation,Message

from .serializers import ConversationSerializer,MessageSerializer
from .paginaters import *
from rest_framework.permissions import IsAuthenticated


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"

    def get_queryset(self):
        queryset = Conversation.objects.filter(
            name__contains=self.request.user.username
        )
        return queryset

    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user}

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'Refresh':str(refresh),
        'access':str(refresh.access_token)
    }
def home(request):
    return render(request,'home.html')

class LoginUserView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = authenticate(username = username, password = password)
        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response({'msg':'the user has been logged in sucessfully','tokens':tokens})
        return Response('The username or password is incorrect')
class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.username,
            )
            .filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset

class PostImageMessageView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,conversation_name):
        serializer = ImageMessageSerializer(data=request.data,context ={'conversation_name':conversation_name,'user':self.request.user})
        serializer.is_valid(raise_exception=True)
        
        
        
        serializer.save()
        return Response(serializer.data)
    
    