from multiprocessing import Process
import main
import logger
import time

logger = logger.ImmediateDiskLogger(
    name = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())) + ".log",
    log_dir = "./",
)

while True:

    p = Process(target=main.main, args=(logger,))
    logger.info("main start ...")
    p.start()
    p.join()
    logger.critical(" main program exit !!!") # 子进程崩溃不影响主进程