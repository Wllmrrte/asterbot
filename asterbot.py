import asyncio
import random
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

# Configuración del cliente
API_ID = 9161657
API_HASH = "400dafb52292ea01a8cf1e5c1756a96a"
PHONE_NUMBER = "+51981119038"
SESSION_NAME = "bot_session"

# Intervalo entre envíos (en segundos)
MIN_INTERVAL = 10  # Mínimo tiempo de espera
MAX_INTERVAL = 350  # Máximo tiempo de espera
SPAM_GROUP_NAME = "spam bot"
CONTROL_GROUP_NAME = "spam bot control"

# Lista de grupos a excluir
EXCLUDED_GROUPS = [
    "TRABAJOS LABS 🧑‍💻",
    "👨🏻‍💻GRUPO GENERAL👨🏻‍💻",
    "Admins >🎖 【𝙻𝙻™】 🎖",
    "Usuarios Valiosos [LINK] 02",
    "�𝙏𝘼𝙁𝙁 𝘿𝙀 𝙇𝙊𝙎 𝙂𝙍𝙐𝙋𝙊𝙎"
]

async def reconnect(client):
    """Intentar reconectar automáticamente si la conexión se pierde."""
    while not client.is_connected():
        try:
            await client.connect()
            print("Reconexión exitosa.")
        except Exception as e:
            print(f"Reconexión fallida: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)

async def send_messages_to_groups(client):
    """Reenvía mensajes desde el grupo 'spam bot' a otros grupos."""
    group_ids = []
    control_group_id = None

    # Obtiene los IDs de los grupos de destino y el grupo de control
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            if dialog.name == CONTROL_GROUP_NAME:
                control_group_id = dialog.id
            elif dialog.name != SPAM_GROUP_NAME and dialog.name not in EXCLUDED_GROUPS:
                group_ids.append(dialog.id)

    if control_group_id is None:
        print("No se encontró el grupo de control.")
        return

    # Itera sobre los mensajes en el grupo 'spam bot'
    while True:
        await reconnect(client)  # Asegurarse de estar conectado
        async for dialog in client.iter_dialogs():
            if dialog.is_group and dialog.name == SPAM_GROUP_NAME:
                async for message in client.iter_messages(dialog, limit=10):
                    for group_id in group_ids:
                        try:
                            await client.forward_messages(group_id, [message])
                            group_name = (await client.get_entity(group_id)).title
                            print(f"\033[92mMensaje reenviado al grupo {group_name}\033[0m")
                            await client.send_message(control_group_id, f"Mensaje reenviado a: {group_name}")
                        except FloodWaitError as e:
                            print(f"\033[91mDemasiados mensajes enviados. Esperando {e.seconds} segundos...\033[0m")
                            await asyncio.sleep(e.seconds)
                        except Exception as e:
                            print(f"\033[91mError al reenviar mensaje al grupo {group_id}: {e}\033[0m")
                            await client.send_message(control_group_id, f"Error al reenviar mensaje al grupo {group_id}.")
                        # Pausa entre reenvíos de mensajes
                        interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
                        await asyncio.sleep(interval)
        # Pausa antes de verificar nuevos mensajes
        await asyncio.sleep(10)

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await reconnect(client)
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            await client.sign_in(PHONE_NUMBER, input("Ingresa el código enviado a tu teléfono: "))

        print("Bot conectado exitosamente.")
        await send_messages_to_groups(client)

if __name__ == "__main__":
    asyncio.run(main())
