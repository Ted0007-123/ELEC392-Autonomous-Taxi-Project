import time

from picarx import Picarx
import math


import numpy as np
import math
from CONTROL_TOOLS_EXT import Ackermann_Kinomatic , AtoB


px = Picarx()
q = np.array([0,0,0])
u = np.array([0,0])
CAR = Ackermann_Kinomatic(state=q,input=u)
CAR.u[0] = CAR.Input(CAR.u[0])
GOAL1 = [40,-60]
GOAL2 = [80,30]
time.time()

T1 = time.time()
if __name__ == "__main__":
    try:
        while True:
            T2 = time.time()
            T = T2 - T1
            #CAR.rk_four(CAR.function, CAR.q, CAR.u, T)
            if T > .2:

                angle,mag = AtoB(GOAL1[0],GOAL1[1],CAR.q[0],CAR.q[1],CAR.headTRUE,R = 20,ANG_CO=.7,MAG_CO=8)
                # angle,mag = [10,10]

                CAR.u = [CAR.Input(mag),angle]
                px.set_dir_servo_angle(-angle)
                px.forward(mag)
                T1 = time.time()

                CAR.rk_four(CAR.function, CAR.q, CAR.u, T)
                print("STATS")
                print(CAR.u)
                print(CAR.q)
                print(CAR.headTRUE)

                if mag == 0:
                    GOAL1 = GOAL2
                    break




    finally:
        px.stop()
        #x=1
