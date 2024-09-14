import cv2
from cvzone.HandTrackingModule import HandDetector

class Button:
    def __init__(self, pos, width, height, val):
        self.pos = pos
        self.width = width
        self.height = height
        self.val = val

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height), (0, 165, 255), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height), (50, 50, 50), 3)
        cv2.putText(img, self.val, (self.pos[0] + 25, self.pos[1] + 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    def is_clicked(self, x, y):
        return self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height

def main():
    try:
        # Initialize webcam capture
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)  # Set width
        cap.set(4, 720)   # Set height

        detector = HandDetector(detectionCon=0.8, maxHands=1)

        # Define the button layout
        b_values = [['7', '8', '9', '*'], ['4', '5', '6', '-'], ['1', '2', '3', '+'], ['0', '.', '/', '=']]
        buttons = [Button((x * 100 + 800, y * 100 + 150), 100, 100, b_values[y][x]) for x in range(4) for y in range(4)]

        eqn = ''
        delay_counter = 0

        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture image from webcam.")
                break

            img = cv2.flip(img, 1)

            # Detect hands and draw buttons
            hands, img = detector.findHands(img, flipType=False)

            # Draw a rectangle where the equation will be displayed
            cv2.rectangle(img, (800, 50), (800 + 400, 70 + 100), (0, 0, 0), cv2.FILLED)
            cv2.rectangle(img, (800, 50), (800 + 400, 70 + 100), (0, 0, 0), 3)

            for button in buttons:
                button.draw(img)

            if hands:
                try:
                    lmList = hands[0]['lmList']
                    if len(lmList) >= 9:  # Ensure at least the index finger tip is detected
                        x1, y1 = lmList[8][:2]  # Index finger tip

                        # Check if the index finger is close to the thumb (indicating a click)
                        thumb_x, thumb_y = lmList[4][:2]  # Thumb tip
                        length, img, _ = detector.findDistance((x1, y1), (thumb_x, thumb_y), img)

                        if length < 50:  # Adjust this value if needed for better accuracy
                            for button in buttons:
                                if button.is_clicked(x1, y1) and delay_counter == 0:
                                    entered_eqn = button.val
                                    if entered_eqn == "=":
                                        try:
                                            eqn = str("{:.2f}".format(eval(eqn)))
                                        except Exception as e:
                                            print(f"Error in equation evaluation: {e}")
                                            eqn = "Error"
                                    else:
                                        eqn += entered_eqn
                                    delay_counter = 1

                except Exception as e:
                    print(f"Error in hand processing: {e}")

            if delay_counter != 0:
                delay_counter += 1
                if delay_counter > 10:
                    delay_counter = 0

            cv2.putText(img, eqn, (810, 120), cv2.FONT_HERSHEY_PLAIN, 3, (0, 165, 255), 3)
            cv2.imshow("Virtual Calculator", img)

            k = cv2.waitKey(1)
            if k == ord('c'):
                eqn = ''
            if k == 27:  # Escape to exit
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
