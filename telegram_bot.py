from telethon import TelegramClient
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.errors import FloodWaitError
import asyncio
import time
import os

# Получаем данные из переменных окружения (безопасно!)
api_id = int(os.getenv('API_ID', '27611286'))
api_hash = os.getenv('API_HASH', '50649b84fb866096d61639d318790961')
phone = os.getenv('PHONE', '+375259620335')

print(f"🚀 Запуск с телефоном: {phone}")

client = TelegramClient('session', api_id, api_hash, connection_retries=9999, auto_reconnect=True)

is_running = True

async def update_status():
    try:
        await client(UpdateStatusRequest(offline=False))
        return True
    except FloodWaitError as e:
        print(f"⏳ FloodWait: ждем {e.seconds} сек")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"❌ Ошибка обновления статуса: {e}")
        await asyncio.sleep(3)
        return False

async def keep_alive():
    while is_running:
        try:
            await client.get_me()
            print("💓 Keep-alive ping")
        except Exception as e:
            print(f"⚠️ Keep-alive ошибка: {e}")
        await asyncio.sleep(60)

async def check_connection():
    global is_running
    while is_running:
        if not client.is_connected():
            print("🔄 Переподключение...")
            try:
                await client.connect()
                print("✅ Переподключено!")
            except Exception as e:
                print(f"❌ Ошибка переподключения: {e}")
                await asyncio.sleep(10)
        await asyncio.sleep(10)

async def main():
    global is_running
    
    try:
        print("📱 Начинаем авторизацию...")
        await client.start(phone)
        me = await client.get_me()
        print(f"✅ Авторизован: {me.first_name} (@{me.username if me.username else 'без username'})")
        print(f"📞 Телефон: {me.phone}")
        print("🟢 ONLINE 24/7 режим активирован!")
        print("-" * 50)
        
        asyncio.create_task(keep_alive())
        asyncio.create_task(check_connection())
        
        count = 0
        
        while is_running:
            try:
                if client.is_connected():
                    success = await update_status()
                    if success:
                        count += 1
                        t = time.strftime('%H:%M:%S')
                        if count % 50 == 0:
                            print(f"[{t}] 🟢 ONLINE | Обновлений: {count}")
                        else:
                            print(f"[{t}] 🟢 ONLINE", end='\r', flush=True)
                
                await asyncio.sleep(4)
                    
            except KeyboardInterrupt:
                print("\n⏹️ Остановка по Ctrl+C...")
                is_running = False
                break
            except Exception as e:
                print(f"❌ Ошибка в главном цикле: {e}")
                await asyncio.sleep(10)
                
    except Exception as e:
        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        is_running = False
        print("👋 Завершение работы...")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Telegram Online Bot by Render")
    print("=" * 50)
    with client:
        client.loop.run_until_complete(main())
