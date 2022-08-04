# ChatApplication-
##This is the apis for the chat application 


##Features of Chat Application


Starting a conversation with a user
Sending and receiving messages and files 
Seeing when a user is typing
Seeing notifications for new messages
Chat scrolling and loading chat history
Reading messages
Authenticated connection

The protocol used in this application are https and websockets.

Basically we use the http protocol inorder to get the all the messages between the sender and reciever.
And we use the websockets protocols inorder to establish the connection between the sender and reciever.This connection will be satefull

Inorder to establish a websockets connection the user must be a authenticated user and the user authentication is done by simple jwt authentication.

If the user is not authenticated or we can say if the user is annonymous then the websockets protocol will send the response like the user is not authenticated user.


The routes are the user inorder to establish the connection is ws:localhost:8000/ws/chat/<conversation_name>/?token='simple_jwt_tokens'
Basically the conversation name is the room name containing the sender and reciever username like this yugan_test

Here yugan is the sender and test is the reciever.

when we will request  ws:localhost:8000/ws/chat/<conversation_name>/?token='simple_jwt_tokens' then we will get 

1.All the last 50 message between the yugan and test 
2.and the user online status in this case yugan is connected to websocket and yugan will be online 

Other important point is that if we want to create a group and want to send the messages to the group then we will request the url like ws:localhost:8000/ws/chat/<group_name>/?token='simple_jwt_tokens'

In this case the conversation_name will be replaced with the group_name and we will provide the group name like 1_2_3 and the user with this ids will be inside the created group 

for example: ws:localhost:8000/ws/chat/<1_2_3>/?token='simple_jwt_tokens'.This will create a group with user with ids 1,2 and 3.

And if we request this url then similarly we will get the last 50 messages and user online status

Now second part is sending messages to a group or user.
if order to send the messages we will send the json objects like this 
{
"type":"chat_message",
"message":"this is just the testing message"
}

we should specify the 'type' here in the json objects

Second case is that if the user is typing the message then in forntend we should send the json like this 
{
"type":"typing"
"typing":"True"
}
"typing" should be a boolean field.

Now last websocket protocol url is of notification.
we should call this url ws:localhost:8000/ws/notification/?token='simple_jwt_token'
This will give the count of unread messages for the requested user.

Now when the user get the new messages and read the message then we should send another json like this 

{
"type":"read_messages"
}

Then in the nofitication url we can see the unread messages updated 

Now we will see the https requests.
Firstly we are going to get the active conversation between the user and reciever.
we get request on the url localhost:8000/conversation/yugan_test
Then we will get the last active messages between the yugan and test 
here yugan_test is the look up field you can give any parameters like yugan_test2 this will show the messages between the yugan and test2.


And if we want to get the chat history between the sender and reciever we call get the url localhost:8000/messages/?conversation=yugan_test
this will return the count and all the messages between the yugan and test.


And lastly we are going to send the files from sender to the reciever and this will be done through the https protocol rather than websockets protocol.
We send the post request to the url localhost:8000/filesmessage/<conversation_name>/ with the  json objects like this:

In form-data format not in json format 
"files":"files drs in your local enviroment"






