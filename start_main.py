from multiprocessing import Process
from main import main
import time

#初始化日志文件
log_file = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())) + "_bs.log"
p = Process(target=main.main, args=(log_file))

p.start()
p.join()
cur_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))

print(f"{cur_time} main program exit !!!")  # 子进程崩溃不影响主进程