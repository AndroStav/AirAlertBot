import asyncio
import math
from alerts_in_ua import AsyncClient as AsyncAlertsClient
import telegram

ALERTSTOKEN = "Alerts_in_ua_token"  #Токен alerts.in.ua api
TGTOKEN = "Telegram_bot_token"      #Токен телеграм бота
CHAT_ID = "Group_chat_id"           #ID групи
THREAD_ID = "Group_thread_id"       #ID гілки в групі

bot = telegram.Bot(TGTOKEN)

async def main():
    alerts_client = AsyncAlertsClient(token=ALERTSTOKEN)
    lastmess = 0
    
    while True:
        try:
            alert_status = await alerts_client.get_air_raid_alert_status(31)
            status_text = alert_status.status

            if "no_alert" in status_text:
                if lastmess == 1:
                    print("Відбій")
                    message = "🟢 Відбій повітряної тривоги 🟢"
                    await bot.send_message(chat_id=CHAT_ID, text=message, message_thread_id=THREAD_ID, read_timeout=60, write_timeout=60, connect_timeout=60)
                    lastmess = 0
                    print("Повідомлення надіслано")
            else:
                if "active" in status_text:
                    if lastmess == 0:
                        print("Тривога")
                        message = "🔴 Увага! Повітряна тривога! 🔴"
                        await bot.send_message(chat_id=CHAT_ID, text=message, message_thread_id=THREAD_ID, read_timeout=60, write_timeout=60, connect_timeout=60)
                        lastmess = 1
                        print("Повідомлення надіслано")
            await asyncio.sleep(60)

        except Exception as e:
            print(f"Виникла помилка: {e}")
            await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())
