import threading
import time
import estop_test

newThread = threading.Thread(target=estop_test.estop, args="FLAG")









def interrupted():
    print("inter")
    sys.exit(0)

try:
    i = 0
    while(1):
        print(i)
        i = i + 1
    
except KeyboardInterrupt:
    interrupted()