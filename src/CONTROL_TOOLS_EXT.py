import numpy as np
import math as math


#THIS IS THE CLASS THAT REPRESENTS THE CAR
#init with the state = [X,Y,heading in deg] and Input = [Volocity cm/s, and steering angle in deg] 

#class  !!!!!!!!!   car !!!!!!!!!!!!!!!

class Ackermann_Kinomatic:         #IE CAR
    # Ackerman Class using inputs of rear wheel velocity(power applied to the motor), and steering angle
    # Constraints assumed to come from both wheel sets
    #
    # (states) q = [X_front,Y_front, Angle_orientation, Angle_steering(respect to orientation)]
    # (inputs) u= [Velocity, ang_steer] {volocity is applied to the back wheels, angle steer at front wheeels}

    # Q = q_derivative = function(u,q)

    def __init__(self,px,state,input,Wheel_Width = 11.5,Wheel_Length = 19.8):#cm
        self.Len = Wheel_Length
        self.Wid = Wheel_Width

        self.q = state #[X,Y,Head]
        self.u = input #[Volocity,steer_angle]
        self.headTRUE = state[2] #This is the real heading
        self.px = px

    """this function represents the derivative of the states based on themselves and the input values"""
    def function(self,q,u):
        f = np.zeros(3)
        f[0] = u[0] * np.cos(np.deg2rad(q[2]))
        f[1] = u[0] * np.sin(np.deg2rad(q[2]))
        f[2] = ((u[0]/self.Len) * np.tan(np.deg2rad(u[1])))

        return f
    '''Converts from input percent power to estimated volocity'''
    def Input(self, Percent):  # From percentage power ret volcity
        if Percent <= 20:
            return Percent * 1.25
        else:
            return 20 * np.exp(Percent * .008703)
            
    '''Converts from volocity to estimated needed power percent'''
    def VoloToPer(self, Volo):
        if Volo > 25.2:
            return Volo / 1.25
        else:
            return np.log(Volo) / (np.log(21) * .008703)
            
    '''a function to integrate the current state and derivative into the next state'''
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
    
    '''another simple function to integrate the current state and derivative into the next state''' 
    def Euler(self, f, q, u, T):
        q_new = q + f(q, u) * T
        self.q = q_new
        return q_new

        
        """Function that handels state change while spinning stationarly""" 
    def Spun(self, P_wheels, T):
        V_wheels = self.Input(P_wheels)
        heading_change = T * V_wheels * 11.5 / (16 * 4)# in deg
        return heading_change   #
    def Spinning(self, P_wheels,T):
        self.px.set_motor_speed(motor = 1, speed = -P_wheels) #Left
        self.px.set_motor_speed(motor = 2, speed = P_wheels) #Right
        
        time.sleep(T)
        self.px.forwards(0) #left
        return()

    def Spin(self, P_wheels, Angle):
        V_wheels = self.Input(P_wheels)
        T = Angle*16*4/(V_wheels*11.5)
        return(T)

    def JustSpinAlready(Angle,Power=10):
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        Spinning(Power,Spin(Power,Angle))
        return()
        
        


#----------------------------------------------------------------------------------------------------------
#_________________________________________________________________________________________________________
'''CHECKS THE GRAYSACLE VALUE IF THERE IS A 'LINE' UNDER IT'''
def Check_Line(reading,High,Low):
    if reading >= Low and reading <= High:
        return 1
    else:
        return 0
'''USES px, the high and low sensor valus for green, and some of the prev values to determine the needed steering angle '''
def Follow_Line(px,Greenhigh,Greenlow,Angle_prev=0,Error_prev=0,Error_sum=0): #1 = on, #0 = off
    grayscale_reading = px.get_grayscale_data()
    Left =  Check_Line(grayscale_reading[0],Greenhigh,Greenlow)
    Center = Check_Line(grayscale_reading[1],Greenhigh,Greenlow)
    Right =  Check_Line(grayscale_reading[2],Greenhigh,Greenlow)

    print(Left,Center,Right)
    print(grayscale_reading)


    Steering_angle =  5 * Left + -5 * Right #negitive deg to the left
    Steering_angle =  Steering_angle - Steering_angle * Center * .35
    Error = Steering_angle

    Error_Change = Error - Error_prev # if error getting worse positive

    if Left == Center == Right == 0:
        # print("fuck")
        Steering_angle = Angle_prev * .5 + Error_prev * .4 + (-Error_Change) * .5
        # print(Error_prev)
        return (Steering_angle, Error_prev)

    Steering_angle = Angle_prev * .3 + Error * .3 + (Error_Change) * .3

    return (Steering_angle, Error)


'''A function that sould be looped to determine if the car is currently riding a line'''    
def On_Line(Gray_reading,Greenhigh=1200,Greenlow=800,Prev_Count = 0,thresh=5):
    Left =  Check_Line(Gray_reading[0],Greenhigh,Greenlow) # 1 on 0 off
    Center = Check_Line(Gray_reading[1],Greenhigh,Greenlow)
    Right =  Check_Line(Gray_reading[2],Greenhigh,Greenlow)
    print("Looking For line")
    if (Left + Center + Right) >= 2: #on line
        Count = Prev_Count + 1
    if (Left + Center + Right) >= 3: #on line              could cause issue  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!       '''''''
        Count = Prev_Count + 1
    else:
        Count = Prev_Count - 1
    Count = np.clip(Count,0,thresh+5)# clamp the value from 0 +

    Riding = 0 #off line
    if Count >= thresh:
        Riding = 1# on line
    return (Count,Riding)
        
    

#========================================================================================================
def AtoB(x_goal,y_goal,x_current,y_current,heading,R = 20,ANG_CO=.5,MAG_CO=1):

    X = x_goal - x_current
    Y = y_goal - y_current


    # print("X,Y current")
    # print(x_current)
    # print(y_current)

    MAG = math.sqrt(X**2 + Y**2)
    Angle = math.degrees(math.atan(Y/X))
    # print("ANGLE")
    # print(Angle)


    #FIX angle based on region position
    if X >=0: # +x,+y,-y
        Angle = Angle
    elif X <0:# -x,+y,-y
        Angle = 180 + Angle

    Error_MAG = MAG
    Error_Angle = Angle - heading
    # if Error_MAG >= 60:
        # Error_Angle = Error_Angle/Error_MAG

    if Error_MAG < R:
        Error_MAG = 0
    # if Error_MAG <20:
    #     ANG_CO = np.clip(ANG_CO, -10,10)
    return (np.clip(Error_Angle,-40,40) * ANG_CO),(np.clip(Error_MAG,0,100) * MAG_CO) #adjustable constant

def Measure_AtoB(x_goal,y_goal,x_current,y_current,heading):

    X = x_goal - x_current
    Y = y_goal - y_current

    MAG = math.sqrt(X**2 + Y**2)
    Angle = math.degrees(math.atan(Y/X))

    #FIX angle based on region position
    if X >=0: # +x,+y,-y
        Angle = Angle
    elif X <0:# -x,+y,-y
        Angle = 180 + Angle

    Error_Mag = MAG
    Error_Angle = Angle - heading

        # if Error_MAG <20:
    #     ANG_CO = np.clip(ANG_CO, -10,10)
    return (Error_Angle,Error_Mag) #adjustable
#-----------------------------------------------------------------------------------------------
#========================================================================================================
#========================================================================================================
'''

# CALL THESE FUNCTIONS
"""px is pixcar class ,CAR is a Akkerman class, dest[x,y], wanted volocity cm/s"""


# Target_H,Target_L grayscale line values limits
def handle_line_following(px, CAR, dest, speed, Target_H=1200, Target_L=800):
    Error_p=0
    Error_s=0
    angle, percent = Follow_Line(px,Target_H,Target_L,Angle_prev=CAR.u[1],)


def What_do():  # The general handling function
    return ()

'''
#-----------------------------------------------------------------------------------------------
