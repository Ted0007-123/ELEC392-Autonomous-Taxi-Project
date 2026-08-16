

#import VPSF
import math
import numpy as np

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


T = .2
q = np.array([0,0,0],dtype=float)
u = np.array([80,10],dtype=float)

#print(np.deg2rad(90))

Car = Ackermann_Kinomatic(state=q,input=u)
Car.u[0] = Car.Input(Car.u[0])
print(Car.u[0])
for i in range(5):
    q_new = Car.rk_four(Car.function,Car.q,Car.u,T)
    #q_new = Car.rk_four(Car.function,Car.q,Car.u,T)

    print("state")
    print(Car.q)
    print(Car.headTRUE)
    print(Car.u)


