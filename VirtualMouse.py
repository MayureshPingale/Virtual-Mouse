import cv2
import numpy as np
import time
import autopy
import HandTracking as ht
import pyautogui


def scroll_horizontal(value):
    pyautogui.keyDown('shift')
    pyautogui.keyDown('ctrl')
    pyautogui.scroll(value)
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('shift')


def zoom_reduce():
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('-')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('-')


def zoom_increase():
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('=')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('=')


def all_value_checker(arr, value):
    for i in arr:
        if i != value:
            return False

    return True


width_camera, height_camera = 640, 480
width_screen, height_screen = pyautogui.size()
print(width_screen, height_screen)
handDetector = ht.HandDetector(maxHands=2, detection_conf=0.85)
capture_frame = cv2.VideoCapture(0)
mouse_pad_frame = 100
smoothening = 10
pyautogui.PAUSE = 0.001
previousTime = 0
previousMouseLocX, previousMouseLocY = 0, 0

capture_frame.set(3, width_camera)
capture_frame.set(4, height_camera)

threshold = 10
isNeutral = False
pinchMode = False
fistMode_activated = False

previousZoomDistance = None

while True:
    flag_video, image = capture_frame.read()
    image = cv2.flip(image, 1)
    image, no_of_hands = handDetector.find_hands(image)
    if no_of_hands == 2:
        print("Two Hands")
        landmarksList1 = handDetector.get_landmarks(image, 0)
        landmarksList2 = handDetector.get_landmarks(image, 1)
        fingers_up1 = handDetector.get_fingers_up(landmarksList1)
        fingers_up2 = handDetector.get_fingers_up(landmarksList2)

        if np.array(fingers_up1[1:]).all() == 1 and np.array(fingers_up2[1:]).all() == 1:
            print("Neutral Mode tWO")
            previousZoomDistance = None

        elif fingers_up1[1] == 1 and fingers_up2[1] == 1:
            print("Zoom Mode")
            currentZoomDistance = abs(landmarksList1[4][1] - landmarksList2[4][1])
            if previousZoomDistance:
                isMove = abs(previousZoomDistance - currentZoomDistance) > 15
                if isMove:
                    if previousZoomDistance > currentZoomDistance:
                        zoom_reduce()
                    else:
                        zoom_increase()

            previousZoomDistance = currentZoomDistance

    elif no_of_hands == 1:
        landmarksList = handDetector.get_landmarks(image, 0)

        cv2.rectangle(image, (mouse_pad_frame, mouse_pad_frame),
                      (width_camera - mouse_pad_frame, height_camera - mouse_pad_frame), (0, 0, 255), 2)

        fingers_up = handDetector.get_fingers_up(landmarksList)
        fingers_down = handDetector.get_fingers_down(landmarksList)
        print(fingers_up)
        distance, image = handDetector.find_distance(8, 12, image, landmarksList, circle_size=7, thickness=2)
        print(distance)

        if fingers_up[0] == 1 and all_value_checker(np.array(fingers_up[1:]), 0):

            if landmarksList[4][1] > landmarksList[17][1]:
                scroll_horizontal(-40)
                print("Right")
            elif landmarksList[6][2] - landmarksList[4][2] > 30:
                isNeutral = False
                print("Up")
                pyautogui.scroll(40)
            else:
                print("Fist Mode Activated")

                if not fistMode_activated:
                    pyautogui.mouseDown(button="left")
                    fistMode_activated = True

                index_x1, index_y1 = landmarksList[4][1:]

                mouse_cord_x = np.interp(index_x1, (mouse_pad_frame, width_camera - mouse_pad_frame), (0, width_screen))
                mouse_cord_y = np.interp(index_y1, (mouse_pad_frame, height_camera - mouse_pad_frame),
                                         (0, height_screen))

                currentX = previousMouseLocX + (mouse_cord_x - previousMouseLocX) / smoothening
                currentY = previousMouseLocY + (mouse_cord_y - previousMouseLocY) / smoothening
                previousMouseLocX, previousMouseLocY = currentX, currentY
                pyautogui.moveTo(currentX, currentY)

        elif np.array(fingers_up[1:]).all():
            print("Neutral Mode")
            isNeutral = True

            if fistMode_activated:
                pyautogui.mouseUp(button="left")
                fistMode_activated = False

        elif np.array(fingers_down[1:]).all() == 1:
            isNeutral = False
            if abs(landmarksList[4][2] - landmarksList[3][2]) <= threshold:
                if landmarksList[4][1] < landmarksList[3][1]:
                    scroll_horizontal(40)
                    print("Left")
        elif fingers_down[0] == 1 and np.array(fingers_down[1:]).all() == 0:
            print("Down")
            pyautogui.scroll(-40)
            isNeutral = False
        elif fingers_up[0] == 1 and fingers_up[1] == 0 and fingers_up[2] == 0:
            isNeutral = False
            print("Up")
            pyautogui.scroll(40)

        elif fingers_up[1] == 1 and fingers_up[2] == 1 and fingers_up[3] == 0 and distance > 20:

            # Moving Mode
            print("Moving Mode")
            index_x1, index_y1 = (landmarksList[8][1] + landmarksList[12][1]) // 2, (
                    landmarksList[8][2] + landmarksList[12][2]) // 2

            mouse_cord_x = np.interp(index_x1, (mouse_pad_frame, width_camera - mouse_pad_frame), (0, width_screen))
            mouse_cord_y = np.interp(index_y1, (mouse_pad_frame, height_camera - mouse_pad_frame), (0, height_screen))

            currentX = previousMouseLocX + (mouse_cord_x - previousMouseLocX) / smoothening
            currentY = previousMouseLocY + (mouse_cord_y - previousMouseLocY) / smoothening
            previousMouseLocX, previousMouseLocY = currentX, currentY

            cv2.circle(image, (index_x1, index_y1), 10, (255, 0, 0), cv2.FILLED)
            pyautogui.moveTo(currentX, currentY)

        elif fingers_up[2] == 1 and fingers_up[1] == 0 and fingers_up[3] == 0 and isNeutral:
            print("Left Click")
            autopy.mouse.click()

        elif fingers_up[1] == 1 and fingers_up[2] == 0 and fingers_up[3] == 0 and isNeutral:
            autopy.mouse.click(autopy.mouse.Button.RIGHT)

            time.sleep(0.5)

    # FPS Calculations
    time_now = time.time()
    frame_per_second = 1 / (time_now - previousTime)
    previousTime = time_now
    cv2.putText(image, str(int(frame_per_second)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Displaying the image
    cv2.waitKey(10)
    cv2.imshow("Img", image)
