import threading
import time
import LED_Control.light_controls as lights
import CONTROL_TOOLS_EXT as contr
import VPFS
# import LineFollower_test

''' line follows only, (untill reaches goal zone of radus r) '''



_can_i_run = False

class Navigation_Line_Travel:
    def __init__(self, controller, carModel,goal,radus=20,speed=20,Timestep=.1):
        self.controller = controller
        self.px = carModel.px
        self.speed = speed
        self.running = False
        self.car = carModel
        self.step = Timestep
        self.goal = [goal[0],goal[1],radus]
        print(goal)

    def start(self):
        self.running = True
        # thread = threading.Thread(target=self._loop, daemon=True)
        # thread.start()

    def _loop(self):
        print("[NAV] navigation test started")
        print("Line Error Setup")
        ERROR_P = 0
        ERROR_S = 0
        current_angle = self.car.u[1] # set up the current angle as the steering angle in the car class
        T1 = time.time()
        T3 = T1
        end_count = 0
        global _can_i_run
        

        while self.running:
            print(self.controller.navigation_allowed)
            if self.controller.navigation_allowed:
                lights.brake_light_off()
                #self.px.set_dir_servo_angle(0)
                Volocity = self.car.Input(self.speed)
                self.car.u[0] = Volocity
                    
                if not _can_i_run:
                    self.px.forward(0)
                else:
                    self.px.forward(self.speed)

                #LineFollower_test.Follow_Line()

                
                
                T2 = time.time()
                T = T2 -T1
                T_up = T2-T3
                if T_up >= 1.0:#UPDATE STATE DATA
                    data =  VPFS.vpfs_whereami()
                    pos_data = data["position"]
                    self.car.q[0]= pos_data[1]#X
                    self.car.q[1]= pos_data[2]#Y
                    self.car.q[2]= pos_data[0]#H

                    T3 = time.time()

                
                    
                if T >= self.step:
                    Angle_car=self.car.q[2]
                    angle, error = contr.Follow_Line(self.car.px, Angle_car, ERROR_P, ERROR_S)
                    self.px.set_dir_servo_angle(-angle)
                    #UPDATE ERRORS
                    Angle_C = angle
                    ERROR_P = error
                    ERROR_S += error
                    #UPDATE MODEL
                    self.car.u[1] = angle
                    self.car.rk_four(self.car.function, self.car.q, self.car.u, self.step)
                    # print(self.car.q)
                    # print(self.car.u)
                    T1 = time.time()
                    
                    angle, mag = contr.AtoB(self.goal[0],self.goal[1],self.car.q[0],self.car.q[1],self.car.q[2],self.goal[2],ANG_CO=.5,MAG_CO=1)

                    #EXIT
                    if mag == 0: # weird exit code to implemnt small movement after hit point
                        end_count +=1
                    if end_count !=0:
                        end_count +=1
                        if end_count >=3:
                            self.stop()

                            


                
            else:
                self.px.stop()
                lights.brake_light_on()
            time.sleep(0.05)


    def stop(self):
        self.running = False
        return(self.car)


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''point where you want to go, carModel class contains the current point'''
class Navigation_AtoB_w_lineDetect_Travel:
    def __init__(self, controller, carModel ,point=[40,40],Timestep=.1,R = 20,  ANG_CO=.5,  MAG_CO=1,threshhold = 5):
        self.controller = controller
        self.px = carModel.px
        self.goal = point
        self.running = False
        self.car = carModel
        self.step = Timestep
        self.thresh = threshhold

    def start(self):
        self.running = True
        # thread = threading.Thread(target=self._loop, daemon=True)
        # thread.start()

    def _loop(self):
        global _can_i_run
        print("[NAV] navigation test started")
        print("Line Error Setup")
        T1 = time.time()
        T3 = T1
        end = 0
        Riding_line = 0
        Line_count = 0

        

        while self.running:

            print(self.controller.navigation_allowed)
            if self.controller.navigation_allowed:
                lights.brake_light_off()
                #self.px.set_dir_servo_angle(0)
                
                #LineFollower_test.Follow_Line()
                
                T2 = time.time()
                T = T2 -T1
                T_up = T2-T3
                if T_up >= 1.0:#UPDATE STATE DATA
                    data =  VPFS.vpfs_whereami()
                    pos_data = data[0]
                    self.car.q[0]= pos_data[1]#X
                    self.car.q[1]= pos_data[2]#Y
                    self.car.q[2]= pos_data[0]#H
                    T3 = time.time()
                    
                if T >= self.step:
                    angle, power_percent = contr.AtoB(x_goal= self.goal[0],  y_goal = self.goal[1],  x_current=self.car.q[0],  y_current=self.car.q[1],  heading =self.car.q[2],R = 20,  ANG_CO=.5,  MAG_CO=1)
                    #test this 
                    if power_percent == 0:
                        end = 1
                        angle = 0
                        power_percent = 5
                        
                    self.car.u = [self.car.Input(power_percent),angle]
                    self.px.set_dir_servo_angle(-angle)
                    self.px.forward(power_percent)
                    #UPDATE ERRORS
                    #UPDATE MODEL
                    self.car.rk_four(self.car.function, self.car.q, self.car.u, self.step)
                    # print(self.car.q)
                    # print(self.car.u)
                    T1 = time.time()
                    print(self.car.q)
                    #CHECK IF ON A LINE
                    if self.thresh >0:
                        Gray_reading = self.car.px.get_grayscale_data()
                        Line_count,Riding_line = contr.On_Line(Gray_reading,Greenhigh=1200,Greenlow=800,Prev_Count = Line_count,thresh=self.thresh)

                    if Riding_line == 1: # on line
                        print("on line")
                        self.stop()
                        
                    
                    
                    if end != 0:# weird logic to let it travel one more time step at lower speed
                        end +=1
                        if end ==2:
                            self.stop()
                            
                        
                        
                        
                        
                    


                
            else:
                self.px.stop()
                lights.brake_light_on()
#            time.sleep(0.05)


    def stop(self):
        self.running = False
        return(self.car)

def get_status(val):
    global _can_i_run
    _can_i_run = val
    return
