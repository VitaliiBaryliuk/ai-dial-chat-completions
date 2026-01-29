import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialCustomClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

deployment_gpt4o = 'gpt-4o'

async def start(stream: bool) -> None:
    dial_client = DialClient(deployment_name=deployment_gpt4o)

    dial_custom_client = DialCustomClient(deployment_name=deployment_gpt4o)

    conversation = Conversation()

    conversation.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))

    while True:
        print("Write your question and press Enter")
        user_input = input("> ").strip()

        if user_input == 'exit':
            print('Goodbye!')
            break

        conversation.add_message(Message(Role.USER, user_input))
        
        if stream:
            response = await dial_custom_client.stream_completion(conversation.get_messages())
        else:
            response = dial_custom_client.get_completion(conversation.get_messages())

        conversation.add_message(response)   


asyncio.run(
    start(True)
)
