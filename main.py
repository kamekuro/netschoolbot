#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2024
#            ✈ https://t.me/kamekuro

# 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit, distribute or redistribute and use for any purpose this file without direct permission from the author.
# All source code is provided for review only.

import logging 
import os; os.system("clear")
if not os.path.exists('config.json'):
    exit("\033[31mОтсутствует файл\033[0m \033[36mconfig.json\033[31m!\033[0m")

import version
import utils; utils.checkConfig()
from commands import routers
from loader import client, patch, scheduler
from utils import middlewares

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d]\n>>> %(message)s\n\n",
    filename="logs.log",
    filemode="w+"
)
patch.include_middleware(middlewares.NoChats())
patch.include_middleware(middlewares.RegUser())

utils.init_db()
utils.printMe()
print("\033[36mИнформация по роутерам:\033[0m")
for router in routers:
    if utils.config['commands'][router.name]:
        patch.include_router(router)
        print(f"\033[32m  • Роутер [{router.name}] успешно добавлен!\033[0m")
        continue
    print(f"\033[31m  • Роутер [{router.name}] отключен.\033[0m")


scheduler.add_job(utils.sendBackup, "interval", seconds=3600)
scheduler.add_job(utils.sendSchedule, "interval", seconds=30)

print(f"\033[36mБот [NetSchool Bot v{'.'.join(list(map(str, list(version.__version__))))}] успешно запущен!\033[0m")
scheduler.start()
client.run()