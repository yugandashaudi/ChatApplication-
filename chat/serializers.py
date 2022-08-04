from django.contrib.auth.models import User 
from rest_framework import serializers

from rest_framework import serializers

from .models import Message,Conversation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]



class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user=serializers.StringRelatedField(many=True)
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "files",
            "timestamp",
            "read",
        )

    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data

   

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    
    class Meta():
       
        fields =['username','password']

class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields=['id','name','other_user','last_message']

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        usernames = obj.name.split("_")
        context = {}
        for username in usernames:
            if username != self.context["user"].username:
                
                # This is the other participant
                other_user = User.objects.get(username=username)
                return UserSerializer(other_user, context=context).data

class ImageMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            'files'
            
           
        
           
            
        )
    def validate(self,arrgs):
        get_conversation_name = self.context.get('conversation_name')
        split_url_params = get_conversation_name.split("_")
        get_user = User.objects.filter(username=split_url_params[1]).first()
        if not get_user:
            raise serializers.ValidationError('The reciever doesnot exits')
        
        conversation_instance = Conversation.objects.filter(name=get_conversation_name).first()

        if not conversation_instance:
            raise serializers.ValidationError('The conversation room doesnot exits')
        return arrgs

    def create(self,validated_data):
        get_conversation_name = self.context.get('conversation_name')
        split_url_params = get_conversation_name.split("_")
        get_user = User.objects.filter(username=split_url_params[1]).first()
        conversation_instance = Conversation.objects.filter(name=get_conversation_name).first()
        create_message = Message.objects.create(from_user=self.context.get('user'),conversation=conversation_instance,files=validated_data.get('files'))
        create_message.to_user.add(get_user)
        create_message.save()
        return create_message




    