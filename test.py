import threading
from threading import Thread

def printX():
    while True:
        print('x')

def printY():
    while True:
        print('y')

def thread_task(lock, choice):
    lock.acquire()
    if choice == 'x':
        printX()
    else:
        printY()
    lock.release()

if __name__ == "__main__":
    choice = input()
    lock = threading.Lock()

    t1 = Thread(target=thread_task, args=(lock,choice,))
    t2 = Thread(target=thread_task, args=(lock,y,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()