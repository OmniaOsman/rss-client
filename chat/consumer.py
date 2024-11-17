# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from .models import ConversationLog, UserQuery
# # from .logic import get_response, find_answer_in_db
# from channels.db import database_sync_to_async


# class ChatbotConsumer(AsyncWebsocketConsumer):
#     @database_sync_to_async
#     def save_conversation_message(self, query, role, message, **kwargs):
#         """Save message to conversation log"""
#         return ConversationLog.objects.create(
#             user=self.user,
#             user_query=query,
#             role=role,
#             message=message,
#             **kwargs
#         )
        
#     async def connect(self):
#         # check if user is authenticated
#         if self.scope["user"].is_anonymous:
#             await self.close()
#             return
        
#         self.user = self.scope["user"]
        
#         # create room name
#         self.room_name = f'chat_room_{self.user.id}'
#         await self.channel_layer.group_add(
#             self.channel_name,
#             self.room_name
#         )

#     async def disconnect(self, close_code):
#         # leave room
#         await self.channel_layer.group_discard(
#             self.channel_name,
#             self.room_name
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
        
#         # Send message to room group
#         # async_to_sync(self.channel_layer.group_send)(
#         #     self.room_name, {"type": "chat_message", "message": message}
#         # )
        
#         # # Get or generate response
#         # bot_response = find_answer_in_db(user_message)
#         # if bot_response is None:
#         #     bot_response = get_response(user_message)
        
#         # Save conversation logs
#         # await self.store_conversation(user_message, bot_response)

#         # Send response back to WebSocket
#         # await self.send(text_data=json.dumps({
#         #     "response": bot_response,
#         # }))

#     async def store_conversation(self, user_message, bot_response):
#         # Replace with actual user ID or fetch user context if necessary
#         user = self.scope["user"]
#         user_query = await database_sync_to_async(UserQuery.objects.create)(
#             user=user, question=user_message, answer=bot_response
#         )
#         await database_sync_to_async(ConversationLog.objects.create)(
#             user=user, message=user_message, user_query=user_query
#         )
#         await database_sync_to_async(ConversationLog.objects.create)(
#             user=user, message=bot_response, is_user_message=False, user_query=user_query
#         )

#     def chat_message(self, event):
#         message = event['message']
        
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))
        