import logging
import os
import asyncio

from business import telegram_bot
from business import discord_bot

from config import discord_config
from config import telegram_config


def main():

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
        level=logging.INFO
    )

    # Setup and run Discor/Telegram bot

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop = asyncio.get_event_loop()

    tasks = []
    discord_token = str(discord_config['token'])
    telegram_token = str(telegram_config['token'])
    logging.info(f'discord token: {discord_token}')
    logging.info(f'telegram token: {telegram_token}')

    if discord_token:
        tasks.append(discord_bot.start_task())

    if telegram_token:
        tasks.append(telegram_bot.start_task())

    try:
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

    # if discord_token:
    #     await asyncio.create_task(discord_bot.start_task())
    # if telegram_token:
    #     logging.info(f'telegram token: {telegram_token}')
    #     await asyncio.create_task(telegram_bot.start_task())


if __name__ == '__main__':
    main()
    # asyncio.run(main())
