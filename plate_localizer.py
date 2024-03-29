import cv2
import numpy as np
import matplotlib.pyplot as plt

class LicensePlateDetector:
    def __init__(self, pth_weights: str, pth_cfg: str, pth_classes: str):
        self.net = cv2.dnn.readNet(pth_weights, pth_cfg)
        self.classes = []
        with open(pth_classes, 'r') as f:
            self.classes = f.read().splitlines()
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.color = (255, 0, 0)
        self.coordinates = None
        self.img = None
        self.fig_image = None
        self.roi_image = None
        self.count = 0


    def detect(self, image: str):
        orig = image
        self.img = orig
        img = orig.copy()
        height, width, _ = img.shape
        blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        output_layer_names = self.net.getUnconnectedOutLayersNames()
        layer_outputs = self.net.forward(output_layer_names)
        boxes = []
        confidences = []
        class_ids = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.1:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)

        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = str(round(confidences[i], 2))
                cv2.rectangle(img, (x,y), (x + w, y + h), self.color, 3)
                cv2.putText(img, label + ' ' + confidence, (x, y + 20), self.font, 1, (255, 255, 255), 1)
                self.coordinates = (x, y, w, h)
                self.crop_plate()
        self.fig_image = img

        # try:
        #    self.coordinates = (x, y, w, h)
        # except:
        #     pass
        return


    def crop_plate(self):
        x, y, w, h = self.coordinates
        roi = self.img[y:y + h, x:x + w]
        self.roi_image = roi
        cv2.imwrite(r"detected_plates\plate_{}.png".format(self.count), roi)
        self.count += 1

        return

def main():
    cap = cv2.VideoCapture("gaadi2.mp4")
    lpd = LicensePlateDetector(
        pth_weights='yolov3-train_final.weights',
        pth_cfg='yolov3_testing.cfg',
        pth_classes='classes.txt'
    )

    while True:
        ret, frame = cap.read()
        lpd.detect(frame)
        cv2.imshow('frame', lpd.fig_image)
        cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

main()