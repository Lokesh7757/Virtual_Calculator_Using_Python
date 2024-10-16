import cv2
from cvzone.HandTrackingModule import HandDetector
import pyttsx3

class Calculator:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def drawbutton(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (125, 125, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        cv2.putText(img, self.value, (self.pos[0] + 30, self.pos[1] + 70), cv2.FONT_HERSHEY_PLAIN,
                    2, (50, 50, 50), 2)

    def Click(self, x, y, img):
        if self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            return True
        else:
            return False

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.say("Please wait! The virtual calculator is starting")
engine.runAndWait()

# Define calculator buttons
buttons = [['7', '8', '9', 'C'],
           ['4', '5', '6', '*'],
           ['1', '2', '3', '+'],
           ['0', '-', '/', '='],
           ['(', ')', '.', 'del']]

buttonList = []
for x in range(4):
    for y in range(5):
        xpos = x * 100 + 700
        ypos = y * 100 + 100
        buttonList.append(Calculator((xpos, ypos), 100, 100, buttons[y][x]))

Equation = ''
Counter = 0

# Webcam setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 1080)
detector = HandDetector(detectionCon=0.9, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    # Draw buttons
    for button in buttonList:
        button.drawbutton(img)

    # Check for hand
    if hands:
        lmList = hands[0]['lmList']  # List of 21 hand landmark positions

        # Find distance between index and middle fingers
        length, info, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)  # Taking only x, y values

        # Get the x, y coordinates of the index finger tip
        x, y = lmList[8][:2]

        # If click is detected (distance between index and middle fingers is small)
        if length < 50 and Counter == 0:
            for i, button in enumerate(buttonList):
                if button.Click(x, y, img):
                    myValue = buttons[int(i % 5)][int(i / 5)]  # Get correct number from buttons list
                    
                    if myValue == '=':
                        try:
                            Equation = str(eval(Equation))
                        except SyntaxError:
                            print("Syntax Error")
                            engine.say("Syntax Error")
                            engine.runAndWait()
                            Equation = 'Syntax Error'
                    elif Equation == 'Syntax Error':
                        Equation = ''
                    elif myValue == 'C':
                        Equation = ''
                    elif myValue == 'del':
                        Equation = Equation[:-1]
                    else:
                        Equation += myValue
                    Counter = 1

    # To avoid multiple clicks
    if Counter != 0:
        Counter += 1
        if Counter > 10:
            Counter = 0

    # Display the result on the screen
    cv2.rectangle(img, (700, 20), (1100, 100), (175, 125, 155), cv2.FILLED)
    cv2.rectangle(img, (700, 20), (1100, 100), (50, 50, 50), 3)
    cv2.putText(img, Equation, (710, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    cv2.putText(img, 'VIRTUAL CALCULATOR -->', (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

    # Show the image in a window
    cv2.imshow("Virtual Calculator", img)
    cv2.moveWindow("Virtual Calculator", 0, 0)

    # Close the webcam on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
