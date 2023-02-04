import time
import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, mode=False, maxHands=2, detection_conf=0.5, track_conf=0.5):
        self.hands_tracking_results = None
        self.mode = mode
        self.maxHands = maxHands
        self.detection_conf = detection_conf
        self.track_conf = track_conf

        # Hand Tracking Objects
        self.mpHan = mp.solutions.hands
        self.hands = self.mpHan.Hands(self.mode, self.maxHands, self.detection_conf, self.track_conf)
        self.draw_hands = mp.solutions.drawing_utils

        self.tip_of_fingers = [4, 8, 12, 16, 20]

    def find_hands(self, image, draw=True):
        no_of_hands = 0
        image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.hands_tracking_results = self.hands.process(image_RGB)

        if self.hands_tracking_results.multi_hand_landmarks:
            for hand in self.hands_tracking_results.multi_hand_landmarks:
                no_of_hands += 1
                if draw:
                    self.draw_hands.draw_landmarks(image, hand, self.mpHan.HAND_CONNECTIONS)

        return image, no_of_hands

    def get_landmarks(self, image, hand_number=0):
        landmarksList = []
        if self.hands_tracking_results.multi_hand_landmarks:
            hand_detected = self.hands_tracking_results.multi_hand_landmarks[hand_number]

            for index, landmarks in enumerate(hand_detected.landmark):
                height, width, channel = image.shape
                pixelsX, pixelsY = int(landmarks.x * width), int(landmarks.y * height)
                landmarksList.append([index, pixelsX, pixelsY])

        return landmarksList

    def get_fingers_up(self, landmarksList):
        fingers_up = []

        if landmarksList:
            if landmarksList[self.tip_of_fingers[0]][1] > landmarksList[self.tip_of_fingers[0] - 1][1]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

            for tip in range(1, len(self.tip_of_fingers)):
                if landmarksList[self.tip_of_fingers[tip]][2] < landmarksList[self.tip_of_fingers[tip] - 2][2]:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)

        return fingers_up

    def get_fingers_down(self, landmarksList):
        fingers_down = []

        if landmarksList:
            for tip in range(0, len(self.tip_of_fingers)):
                if landmarksList[self.tip_of_fingers[tip]][2] > landmarksList[self.tip_of_fingers[tip] - 1][2]:
                    fingers_down.append(1)
                else:
                    fingers_down.append(0)

        return fingers_down


    def find_distance(self, point1, point2, image, landmarks, draw=True, circle_size=10, thickness=5):
        x1, y1 = landmarks[point1][1:]
        x2, y2 = landmarks[point2][1:]

        if draw:
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), thickness)
            cv2.circle(image, (x1, y1), circle_size, (255, 0, 0), cv2.FILLED)
            cv2.circle(image, (x2, y2), circle_size, (255, 0, 0), cv2.FILLED)

        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance, image