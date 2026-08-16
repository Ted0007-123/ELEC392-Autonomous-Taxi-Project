import threading
import time
import LED_Control.light_controls as lights
import navigation_objects as moveType
import CONTROL_TOOLS_EXT as contr
import numpy as np
from picarx import Picarx

# import LineFollower_test

        
"""Function that handels state change while spinning stationarly""" 
# def Spun(car, P_wheels, T):
#     V_wheels = self.Input(P_wheels)
#     heading_change = T * V_wheels * 11.5 / (16 * 4)# in deg
#     return heading_change   #
# def Spinning( car, P_wheels,T):
#     car.px.set_motor_speed(motor = 1, speed = -P_wheels) #Left
#     car.px.set_motor_speed(motor = 2, speed = -P_wheels) #Right
    
#     time.sleep(T)
#     car.px.forwards(0) #left
#     return()

# def Spin(car, P_wheels, Angle):
#     V_wheels = car.Input(P_wheels)
#     T = Angle*16*4/(V_wheels*11.5)
#     return(T)

def Just_spin_plz(car):
        print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
        px = car.px
        px.set_dir_servo_angle(-20)
        px.forward(20)
        time.sleep(.1)
        px.set_dir_servo_angle(-30)
        px.forward(20)
        time.sleep(1.4)
        px.set_dir_servo_angle(30)
        px.backward(20)
        time.sleep(1.3)
        px.stop()
        px.set_dir_servo_angle(-27)
        px.forward(22)
        time.sleep(1.1)
        #return()
        px.stop()













def handel_straight(controller,carModel,goal,radus=40,speed=20,Timestep=.1):
    print(np.ones(10000))
    GO = moveType.Navigation_Line_Travel(controller,carModel,goal,radus,speed,Timestep)
    GO.start()
    Car=GO._loop()
    
    return(Car)
def handel_left(controller,carModel,goal,radus=40,speed=20,Timestep=.1):
    print(np.ones(10000)*2)

    GO = moveType.Navigation_AtoB_w_lineDetect_Travel( controller, carModel ,point=[100+carModel.u[0],100+carModel.u[1]],Timestep=.1,R = 50,  ANG_CO=.5,  MAG_CO=1,threshhold = 5) #__init__(self, controller, carModel ,point=[40,40],Timestep=.1,R = 20,  ANG_CO=.5,  MAG_CO=1,threshhold = 5):
    GO.start()
    Car=GO._loop()
    
    
    GO2 = moveType.Navigation_Line_Travel(controller,carModel,goal,radus,speed,Timestep)
    GO2.start()
    Car=GO2._loop()
    return(Car)
def handel_right(controller,carModel,goal,radus=40,speed=20,Timestep=.1):
    print(np.ones(10000)*3)

    GO = moveType.Navigation_AtoB_w_lineDetect_Travel(controller, carModel ,point=[90+carModel.u[0],-90+carModel.u[1]],Timestep=.1,R = 40,  ANG_CO=.7,  MAG_CO=1.2,threshhold = 5) #__init__(self, controller, carModel ,point=[40,40],Timestep=.1,R = 20,  ANG_CO=.5,  MAG_CO=1,threshhold = 5):
    GO.start()
    Car=GO._loop()
    

    GO2 = moveType.Navigation_Line_Travel(controller,carModel,goal,radus,speed,Timestep)
    GO2.start()
    Car=GO2._loop()
    return(Car)
def handel_spin(controller,carModel,goal,radus=40,speed=20,Timestep=.1):
    print(np.ones(10000)*4)
    print(carModel.px)

    Just_spin_plz(carModel)#,Angle=145,Power=100)
    data =  VPFS.vpfs_whereami()
    pos_data = data[0]
    self.car.q[0]= pos_data[1]#X
    self.car.q[1]= pos_data[2]#Y
    self.car.q[2]= pos_data[0]#H
    GO = moveType.Navigation_Line_Travel(controller,carModel,goal,radus,speed,Timestep)
    GO.start()
    Car=GO._loop()
    return(Car)

    

#     GO2 = moveType.Navigation_Line_Travel(controller,carModel,goal,radus,speed,Timestep)
#     return(Car)

# def other_left():
# def other_right():
    




class NavigationHandle:
    def __init__(self,controller,CAR,Points,Phase):
        self.controller = controller#?
        self.px = controller.px
        self.running = False
        self.car = CAR
        self.points_list = Points
        print("HAND")
        print(np.zeros(100))
        print("HAND")
        print(Points)
       # CAR.px.set_motor_speed(motor = 2, speed = 40) #Right



        
        

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        print("[NAV] navigation handling started")
        print("Creating Movement classes")
        # LINE = moveType.Navigation_Line_Travel(self.controller, self.car,goal,radus=20,speed=20,Timestep=.1)
        # AtoB = moveType.Navigation_AtoB_simple_Travel(self.controller, self.car ,point=[40,40],Timestep=.1)
        

        

        while self.running:
            
            if self.controller.navigation_allowed:
                print(np.zeros(100))
                print(self.car.u)
                for target in self.points_list:
                    print(target)
                    Measured_Mag,Measured_Ang = contr.Measure_AtoB(target[0],target[1],self.car.q[0],self.car.q[1],self.car.q[2])
                    print(np.ones(100)*9) 
                    print(Measured_Mag,Measured_Ang)

                    print(Measured_Mag,Measured_Ang)
                    self.car=handel_straight(self.controller,self.car,target)

                    if abs(Measured_Ang) <= 40: #change of odd
                        print("straight")
                        self.car=handel_straight(self.controller,self.car,target)
                    if 100 < Measured_Ang > 40 :
                        print("Left")
                        self.car=handel_left(self.controller,self.car,target)
                    if -100 > Measured_Ang < -40 :
                        print("Right")
                        self.car=handel_right(self.controller,self.car,target)
                    else:
                        print("spin")
                        handel_spin(self.controller,self.car,target)
                        
                        
                

            else:
                self.px.stop()
                lights.brake_light_on()
            time.sleep(0.05)


    def stop(self):
        self.running = False
        self.px.stop()
