'''
    Line Following program for Picar-X:

    Pay attention to modify the reference value of the grayscale module
    according to the practical usage scenarios.
    Auto calibrate grayscale values:
        Please run ./calibration/grayscale_calibration.py
    Manual modification:
        Use the following:
            px.set_line_reference([1400, 1400, 1400])
        The reference value be close to the middle of the line gray value
        and the background gray value.

'''
import time

from PIL.ImageOps import grayscale
from PIL.PSDraw import ERROR_PS
from picarx import Picarx
from time import sleep


Greenlow = 800
Greenhigh = 1100
px = Picarx()
# px = Picarx(grayscale_pins=['A0', 'A1', 'A2'])

# Please run ./calibration/grayscale_calibration.py to Auto calibrate grayscale values
# or manual modify reference value by follow code
# px.set_line_reference([1400, 1400, 1400])

def Check_Line(reading,High,Low):
    if reading >= Low and reading <= High:
        return 1
    else:
        return 0
def Follow_Line(Error_prev=0,Error_sum=0): #1 = on, #0 = off
    grayscale_reading = px.get_grayscale_data()
    Left =  Check_Line(grayscale_reading[0],Greenhigh,Greenlow)
    Center = Check_Line(grayscale_reading[1],Greenhigh,Greenlow)
    Right =  Check_Line(grayscale_reading[2],Greenhigh,Greenlow)

    if Left and Center and Right == 0:
        print("fuck")

    Steering_angle =  10 * Left + -10 * Right #negitive deg to the left
    Steering_angle =  Steering_angle - Steering_angle * Center * .35

    Error = Steering_angle

    Error_Change = Error - Error_prev # if error getting worse positive

    Steering_angle = Steering_angle + Error_Change * Steering_angle * .3


    return (Steering_angle,Error)


F_speed = 10

a=1
ERROR_P = 0
ERROR_S = 0
while a==1 :
    angle,error = Follow_Line(ERROR_P,ERROR_S)
    px.set_dir_servo_angle(angle)
    ERROR_P = error
    px.forward(F_speed)
    time.sleep(.01)













