import pycron
import time

"""
cron : 특정한 시간에  지정한 func 수행.
pycron :   특정한 시간이 되었는지 확인함.
"""

if __name__ == "__main__" :
    while(1):
        if ( pycron.is_now('12,13 * * * *') ):
            print("pycron returns....")
        else:
            print("zzzzz")

        time.sleep(10)
