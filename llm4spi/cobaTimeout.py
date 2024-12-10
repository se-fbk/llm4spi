import time
from func_timeout import func_timeout, FunctionTimedOut

def foo(k):
    while k>0:
        print(f">>> {k}")
        time.sleep(1)
        k = k -1
    return k

def goo(k):
    try:
        xx = func_timeout(3, foo, args=[k])
        print(f">>> result:{xx}")
    except FunctionTimedOut:
        print("TIME OUT")


goo(5)