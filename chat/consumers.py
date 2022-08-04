import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *
from .serializers import *

import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None


   

    def connect(self):
        self.accept()
        self.user = self.scope.get('user')
        
        token_check=self.scope.get('expired')
        if token_check:
            return self.send(text_data=json.dumps({'msg':'the token is expired'}))
        if not self.user:
            return self.send(text_data=json.dumps({'msg':'You are not authenticated user'}))
        

        
        self.conversation_name = f"{self.scope['url_route']['kwargs']['conversation_name']}"
       
        self.conversation, created = Conversation.objects.get_or_create(name=self.conversation_name)
       

        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )
       

        async_to_sync(self.channel_layer.group_send)(
        self.conversation_name,
        {
        "type": "user_join",
        "user": self.user.get('user_id'),
        },
)

        self.conversation.online.add(self.user.get('user_id'))
        self.send_json(
        {
        "type": "online_user_list",
        "users": [user.username for user in self.conversation.online.all()],
        }  
        )
        print(user.username for user in self.conversation.online.all())
        messages = self.conversation.messages.all().order_by("-timestamp")[0:50]
        message_count = self.conversation.messages.all().count()
        
        self.send_json({
        "type": "last_50_messages",
        "messages": MessageSerializer(messages, many=True).data,
        "has_more": message_count > 50,
        })
       

    def disconnect(self, code):
        self.user = self.scope.get('user')
        if self.user:
        # send the leave event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "user_leave",
                    "user": self.user.get('user_id'),
                },
            )
            print(self.user.get('user_id'))
            self.conversation.online.remove(self.user.get('user_id'))
        return super().disconnect(code)

    def receive_json(self,content,**kwargs):
        self.user = self.scope.get('user')
       
        
        message_type = content["type"]
        if message_type == "chat_message":
            print(self.get_receiver()[0])
            data = self.get_receiver()
            
            
            message = Message.objects.create(
            from_user=User.objects.get(id=self.user.get('user_id')),
            
            content=content["message"],
            conversation=self.conversation)
            message.to_user.add(*data)
            message.save()
            username = User.objects.get(id=self.user.get('user_id')).username

            async_to_sync(self.channel_layer.group_send)(
            self.conversation_name,
            {
                "type": "chat_message_echo",
                "name": username,
                "message": MessageSerializer(message).data,
            },
            )
            value =self.get_receiver()
            if len(value)==1:
                receiver_name = User.objects.get(id=value[0])
            
                notification_group_name =  receiver_name.username + "__notifications"
                print(notification_group_name)
                
                async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "name": username,
                    "message": MessageSerializer(message).data,
                },
                )
            if len(value)>1:
                group_reciever_username = User.objects.filter(pk__in=self.get_receiver())
                for user in group_reciever_username:
                    notification_group_name = user.username + "__notifications"
                    
                    async_to_sync(self.channel_layer.group_send)(
                    notification_group_name,
                    {
                        "type": "new_message_notification",
                        "name": username,
                        "message": MessageSerializer(message).data,
                    },
                    )

        if message_type == "typing":
            async_to_sync(self.channel_layer.group_send)(
            self.conversation_name,
            {
                "type": "typing",
                "user": username,
                "typing": content["typing"],
            },
            )

        
        if message_type == "read_messages":
            messages_to_me = self.conversation.messages.filter(to_user=self.user.get('user_id'))
            messages_to_me.update(read=True)

            # Update the unread message count
            unread_count = Message.objects.filter(to_user=self.user.get('user_id'), read=False).count()
            username = User.objects.get(id =self.user.get('user_id')).username 
            async_to_sync(self.channel_layer.group_send)(
            username + "__notifications",
            {
                "type": "unread_count",
                "unread_count": unread_count,
            },
            )
        
    def get_receiver(self):
        self.user = self.scope.get('user')
       
        usernames = self.conversation_name.split("_") 
        print(usernames) 
        try:
            split_username = [int(i) for i in usernames]
            print(split_username)
            al_required_username = User.objects.filter(pk__in=split_username)
            print(al_required_username)
            for username in al_required_username:
                
                if username.username == User.objects.get(id=self.user.get('user_id')).username:
                    id = User.objects.get(username=username.username).id
                    print(id)
                    split_username.remove(id)
            return split_username
        except:
            for username in usernames:
                if username != User.objects.get(id=self.user.get('user_id')).username:
                    username_list =[]
                    user = User.objects.get(username=username)
                    username_list.append(user.id)
                    # This is the receiver
                    return username_list

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncoder)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)

    def typing(self, event):
        self.send_json(event)

    def chat_message_echo(self,event):
        self.send_json(event)
    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)

class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.notification_group_name=None

    def connect(self):
        self.user = self.scope.get('user')
        current_user = User.objects.get(id=self.user.get('user_id'))
        if not current_user:
            return 
        self.accept()
        unread_message = Message.objects.filter(to_user=self.user.get('user_id'),read=False).count()
        self.send_json(
            {
                'type':'unread_count',
                'unread_count':unread_message
            }
        )
        username = User.objects.get(id = self.user.get('user_id'))
        self.notification_group_name = username.username + "__notifications"
        print(self.notification_group_name)
        async_to_sync(self.channel_layer.group_add)(
        self.notification_group_name,
        self.channel_name,
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def new_message_notification(self, event):
        self.send_json(event)
    def unread_count(self, event):
        self.send_json(event)