
import navigation_objects as GO
from picarx import Picarx
import threading
import time
import LED_Control.light_controls as lights
import CONTROL_TOOLS_EXT as contr
import VPFS
px = Picarx()
CAR = contr.Ackermann_Kinomatic(px,[0,0,0],[0,0])#__init__(self,px,state,input,Wheel_Width = 11.5,Wheel_Length = 19.8):
print("here 1")
class MainController:
    def __init__(self):
        self.px = None

        # system state
        self.mode = "MANUAL"
        self.navigation_allowed = True
controller = MainController()
print("here 1")
#go = GO.Navigation_AtoB_w_lineDetect_Travel( controller, carModel= CAR ,point=[90,-90],Timestep=.1,R = 40,ANG_CO=.7,MAG_CO=1.2, threshhold = -1)
go = GO.Navigation_Line_Travel(controller,CAR,[80,0],radus=40,speed=20,Timestep=.1)

print("here 2")

go.start()
if __name__ == "__main__":
    try:
        while True:


            go._loop()




    finally:
        px.stop()
