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


Greenlow = 900
Greenhigh = 1200
px = Picarx()
#pi = Picarx()
# px = Picarx(grayscale_pins=['A0', 'A1', 'A2'])

# Please run ./calibration/grayscale_calibration.py to Auto calibrate grayscale values
# or manual modify reference value by follow code
# px.set_line_reference([1400, 1400, 1400])

def Check_Line(reading,High,Low):
    if reading >= Low and reading <= High:
        return 1
    else:
        return 0
def Follow_Line(Angle_prev=0,Error_prev=0,Error_sum=0): #1 = on, #0 = off
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
        print("fuck")
        Steering_angle = Angle_prev * .5 + Error_prev * .4 + (-Error_Change) * .5
        print(Error_prev)
        return (Steering_angle, Error_prev)

    Steering_angle = Angle_prev * .3 + Error * .3 + (Error_Change) * .3

    return (Steering_angle, Error)


if __name__ == "__main__":
    try:
        F_speed = 5
        ERROR_P = 0
        ERROR_S = 0
        Angle_C = 0

        while True:
            angle, error = Follow_Line(Angle_C, ERROR_P, ERROR_S)
            px.set_dir_servo_angle(-angle)
            Angle_C = angle
            ERROR_P = error
            ERROR_S += error
            print(error, ERROR_P)
            px.forward(F_speed)
            time.sleep(.1)


    finally:
        px.stop()
