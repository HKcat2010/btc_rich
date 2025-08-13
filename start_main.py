from multiprocessing import Process
from main import main
import logger
import time

#初始化日志文件
logger = logger.SingletonLogger()

while True:

    p = Process(target=main.main, args=(logger))
    p.start()
    p.join()
    logger.critical(" main program exit !!!") # 子进程崩溃不影响主进程