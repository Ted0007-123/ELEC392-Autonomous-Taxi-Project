





#import VPSF
import math
import time

import numpy as np
from picarx import Picarx


class Ackermann_Kinomatic:
    # Ackerman Class using inputs of rear wheel velocity(power applied to the motor), and steering angle
    # Constraints assumed to come from both wheel sets
    #
    # (states) q = [X_front,Y_front, Angle_orientation, Angle_steering(respect to orientation)]
    # (inputs) u= [Velocity, ang_steer] {volocity is applied to the back wheels, angle steer at front wheeels}

    # Q = q_derivative = function(u,q)

    def __init__(self,state,input,Wheel_Width = 11.5,Wheel_Length = 9.8):#cm
        self.Len = Wheel_Length
        self.Wid = Wheel_Width

        self.q = state #[X,Y,Head]
        self.u = input #[Volocity,steer_angle]
        self.headTRUE = state[2]

    def function(self,q,u):
        f = np.zeros(3)
        f[0] = u[0] * np.cos(np.deg2rad(q[2]))
        f[1] = u[0] * np.sin(np.deg2rad(q[2]))
        f[2] = ((u[0]/self.Len) * np.tan(np.deg2rad(u[1])))
        #print("check for vanishing")
        # print(f[0])
        # print(f[1])
        # print(f[2])
        # print()
        return f

    def Input(self, Percent):  # ret volcity
        if Percent <= 20:
            return Percent * 1.25
        else:
            return 20 * np.exp(Percent * .008703)

    def VoloToPer(self, Volo):
        if Volo > 25.2:
            return Volo / 1.25
        else:
            return np.log(Volo) / (np.log(21) * .008703)

    def rk_four(self,f,q,u,T):
        # print("Ks")
        q[2] = q[2]
        k_1 = f(q, u)
        # print(k_1)
        k_2 = f(q + T / 2.0 * k_1, u)
        # print(k_2)
        k_3 = f(q + T / 2.0 * k_2, u)
        # print(k_3)
        k_4 = f(q + T * k_3, u)
        # print(k_4)
        q_new = np.zeros(3)

        q_new[0] = q[0] + (T / 6.0 * (k_1 + 2.0 * k_2 + 2.0 * k_3 + k_4))[0]
        q_new[1] = q[1] + (T / 6.0 * (k_1 + 2.0 * k_2 + 2.0 * k_3 + k_4))[1]
        q_new[2] = q[2] + np.rad2deg((T / 6.0 * (k_1 + 2.0 * k_2 + 2.0 * k_3 + k_4))[2])

        self.q = q_new
        self.headTRUE = self.headTRUE + (q_new[2] - q[2]) / 2
        return q_new

    def Euler(self, f, q, u, T):
        q_new = q + f(q, u) * T
        self.q = q_new
        return q_new

    def SPIN(self, V_wheels, T):
        heading_change = T * V_wheels * 11.5 / (16 * 4)
        return heading_change

#----------------------------------------------------------------------------------------
def AtoB(x_goal,y_goal,x_current,y_current,heading,ANG_CO=.15,MAG_CO=.8):

    X = x_goal - x_current
    Y = y_goal - y_current


    print("X,Y current")
    print(x_current)
    print(y_current)

    MAG = math.sqrt(X**2 + Y**2)
    Angle = math.degrees(math.atan(Y/X))
    print(Angle)


    #FIX angle based on region position
    if X >=0: # +x,+y,-y
        Angle = Angle
    elif X <0:# -x,+y,-y
        Angle = 180 + Angle

    Error_MAG = MAG
    Error_Angle = Angle - heading

    if Error_MAG < 5:
        Error_MAG = 0
    return (Error_Angle * ANG_CO),(Error_MAG * MAG_CO) #adjustable constant

#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
q = np.array([0,0,0])
u = np.array([0,0])
CAR = Ackermann_Kinomatic(state=q,input=u)
CAR.u[0] = CAR.Input(CAR.u[0])
GOAL1 = [60,20]
GOAL2 = [80,30]
px = Picarx()
time.time()

T1 = time.time()
if __name__ == "__main__":
    try:
        while True:
            T2 = time.time()
            T = T2 - T1
            #CAR.rk_four(CAR.function, CAR.q, CAR.u, T)
            if T > .2:

                angle,mag = AtoB(GOAL1[0],GOAL1[1],CAR.q[0],CAR.q[1],CAR.headTRUE)
                CAR.u = [CAR.Input(mag),angle]
                px.set_dir_servo_angle(-angle)
                px.forward(mag)
                T1 = time.time()
                CAR.rk_four(CAR.function, CAR.q, CAR.u, T)

                if mag == 0:
                    GOAL1 = GOAL2




    finally:
        px.stop()
