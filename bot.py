import asyncio
import math
from alerts_in_ua import AsyncClient as AsyncAlertsClient
from telegram.request import HTTPXRequest
import telegram
import subprocess
import json
from datetime import datetime
import logging

ALERTSTOKEN = "Alerts_in_ua_token"  #Токен alerts.in.ua api
TGTOKEN = "Telegram_bot_token"      #Токен телеграм бота
CHAT_ID = "Group_chat_id"           #ID групи
THREAD_ID = "Group_thread_id"       #ID гілки в групі
lastmess = 0
lasteppo = 0

trequest = HTTPXRequest(connection_pool_size=20)
bot = telegram.Bot(TGTOKEN, request=trequest)

logging.basicConfig(level=logging.DEBUG, filename="bot.log", filemode="w", format="%(asctime)s %(levelname)s [%(funcName)s]: %(message)s")

async def sendmess(message):
    while True:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, message_thread_id=THREAD_ID, read_timeout=60, write_timeout=60, connect_timeout=60)
            logging.info("Повідомлення надіслано")
            return
        
        except telegram.error.TelegramError as e:
            logging.error(e)
            logging.debug("Засинаю після помилки Telegram")
            await asyncio.sleep(15)

        except asyncio.CancelledError as e:
            logging.error(e)
            logging.debug("Засинаю після помилки CancelledError")
            await asyncio.sleep(15)

        except Exception as e:
            logging.error(e)
            logging.debug("Засинаю після помилки")
            await asyncio.sleep(15)

async def eppo():
    global lastmess
    global lasteppo
    target = "Повітряна загроза рухається у вашому напрямку"
    logging.info("Запущено єппо")

    while True:

        if lastmess == 0:
            logging.info("Єппо завершує свою роботу")
            return

        try:
            logging.debug("Перевірка наявності сповіщення від єппо")
            result = subprocess.run(['termux-notification-list'], capture_output=True, text=True)
            notifications = json.loads(result.stdout)

            for notification in notifications:
                if target in notification['content']:
                    messtime = notification['when']

                    if isinstance(messtime, str):
                        messtime = int(datetime.strptime(messtime, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

                    if messtime > lasteppo:
                        logging.info("Загроза наближається!")

                        message = "❗️ Повітряна загроза рухається у нашому напрямку! ❗️"
                        await sendmess(message)
                        
                        logging.info("Повідомлення надіслано")
                        lasteppo = messtime
                        logging.debug(f"lasteppo == {lasteppo}")

            logging.debug("Засинаю")
            await asyncio.sleep(15)

        except asyncio.CancelledError as e:
            logging.error(e)
            logging.debug("Засинаю після помилки CancelledError")
            await asyncio.sleep(15)

        except Exception as e:
            logging.error(e)
            logging.debug("Засинаю після помилки")
            await asyncio.sleep(15)


async def main():
    alerts_client = AsyncAlertsClient(token=ALERTSTOKEN)
    global lastmess
    logging.info("Бот запущено")
    
    while True:
        try:
            logging.debug("Надсилання запиту на alerts.in.ua")
            alert_status = await alerts_client.get_air_raid_alert_status(31)
            status_text = alert_status.status
            logging.debug(f"Отримано повідомлення: {status_text}")

            if "no_alert" in status_text:
                if lastmess == 1:
                    logging.info("Відбій")
                    message = "🟢 Відбій повітряної тривоги 🟢"
                    await sendmess(message)
                    lastmess = 0
                    logging.debug(f"lastmess == {lastmess}")
            else:
                if "active" in status_text:
                    if lastmess == 0:
                        logging.info("Тривога")
                        message = "🔴 Увага! Повітряна тривога! 🔴"
                        await sendmess(message)
                        lastmess = 1
                        logging.debug(f"lastmess == {lastmess}")

                        logging.info("Запуск єппо")
                        asyncio.create_task(eppo())

            logging.debug("Засинаю")
            await asyncio.sleep(60)

        except asyncio.CancelledError as e:
            logging.error(e)
            logging.debug("Засинаю після помилки CancelledError")
            await asyncio.sleep(15)

        except Exception as e:
            logging.error(e)
            logging.debug("Засинаю після помилки")
            await asyncio.sleep(15)


if __name__ == "__main__":    
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            logging.critical(e)
            logging.debug("Засинаю після критичної помилки")
            asyncio.sleep(15)
