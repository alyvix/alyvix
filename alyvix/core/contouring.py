import copy
import numpy as np
import cv2


class ContouringManager:

    def __init__(self, canny_threshold1, canny_threshold2, canny_apertureSize,
                 hough_threshold, hough_minLineLength, hough_maxLineGap,
                 line_angle_tolerance, ellipse_width, ellipse_height,
                 text_roi_emptiness, text_roi_proportion, image_roi_emptiness,
                 vline_hw_proportion, vline_w_maxsize, hline_wh_proportion,
                 hline_h_maxsize, rect_w_minsize, rect_h_minsize,
                 rect_w_maxsize_01, rect_h_maxsize_01, rect_w_maxsize_02,
                 rect_h_maxsize_02, rect_hw_proportion, rect_hw_w_maxsize,
                 rect_wh_proportion, rect_wh_h_maxsize, hrect_proximity,
                 vrect_proximity, vrect_others_proximity,
                 hrect_others_proximity):

        self._original = None
        self._debug_image = None
        self._debug_matrix = None

        self._i = None
        self._r = None
        self._t = None

        self.irt = None

        self._imageBoxes = []
        self._rectBoxes = []
        self._textBoxes = []

        self.canny_threshold1 = canny_threshold1
        self.canny_threshold2 = canny_threshold2
        self.canny_apertureSize = canny_apertureSize
        self.hough_threshold = hough_threshold
        self.hough_minLineLength = hough_minLineLength
        self.hough_maxLineGap = hough_maxLineGap
        self.line_angle_tolerance = line_angle_tolerance
        self.ellipse_width = ellipse_width
        self.ellipse_height = ellipse_height
        self.text_roi_emptiness = text_roi_emptiness
        self.text_roi_proportion = text_roi_proportion
        self.image_roi_emptiness = image_roi_emptiness
        self.vline_hw_proportion = vline_hw_proportion
        self.vline_w_maxsize = vline_w_maxsize
        self.hline_wh_proportion = hline_wh_proportion
        self.hline_h_maxsize = hline_h_maxsize
        self.rect_w_minsize = rect_w_minsize
        self.rect_h_minsize = rect_h_minsize
        self.rect_w_maxsize_01 = rect_w_maxsize_01
        self.rect_h_maxsize_01 = rect_h_maxsize_01
        self.rect_w_maxsize_02 = rect_w_maxsize_02
        self.rect_h_maxsize_02 = rect_h_maxsize_02
        self.rect_hw_proportion = rect_hw_proportion
        self.rect_hw_w_maxsize = rect_hw_w_maxsize
        self.rect_wh_proportion = rect_wh_proportion
        self.rect_wh_h_maxsize = rect_wh_h_maxsize
        self.hrect_proximity = hrect_proximity
        self.vrect_proximity = vrect_proximity
        self.vrect_others_proximity = vrect_others_proximity
        self.hrect_others_proximity = hrect_others_proximity

    def auto_contouring(self, image, scaling_factor=1):

        self._original = image.copy()
        self._debug_image = image.copy()

        self.test = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)

        self._i = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
        self._r = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
        self._t = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)

        debug_i = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
        debug_r = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)
        debug_t = np.zeros((image.shape[0], image.shape[1], 1), np.uint8)

        img = cv2.resize(image, (0, 0), fx=1 / scaling_factor, fy=1 / scaling_factor)

        edges = cv2.Canny(img.copy(),
                          threshold1=self.canny_threshold1,
                          threshold2=self.canny_threshold2,
                          apertureSize=self.canny_apertureSize,
                          L2gradient=True) # PARAM 1, 2, 3: canny_threshold1, canny_threshold2, canny_apertureSize # algoritmo canny

        edges_ori = edges.copy()
        bw = edges.copy()

        lines = cv2.HoughLinesP(edges.copy(),
                                rho=1,
                                theta=np.pi / 180,
                                threshold=self.hough_threshold,
                                minLineLength=self.hough_minLineLength,
                                maxLineGap=self.hough_maxLineGap) # PARAM 4, 5, 6: arg4, arg5, arg6 # indentificazione linee

        if lines is None:
            lines = []

        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                if abs(angle) <= 0+self.line_angle_tolerance or abs(angle) >= 90-self.line_angle_tolerance:
                    cv2.line(bw, (x1, y1), (x2, y2), (0, 0, 0), 3) # PARAM 7: arg5 # cancellazione linee orizzontali verticali
                #     cv2.line(self.test, (x1, y1), (x2, y2), (0, 0, 255), 3)
                # else:
                #     cv2.line(self.test, (x1, y1), (x2, y2), (0, 255, 0), 3)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.ellipse_width, self.ellipse_height)) # PARAM 8, 9: arg1, arg2 # ellisse cancella bordi
        bw = cv2.morphologyEx(bw, cv2.MORPH_GRADIENT, kernel)

        contours, hierarchy = cv2.findContours(bw.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]

        boundingBoxes = sorted(boundingBoxes, key=lambda element: (element[1], element[0]))

        bw_copy = bw.copy()

        self._textBoxes = []

        for i, box in enumerate(boundingBoxes):

            x, y, w, h = box

            area = w * h

            roi_img = bw[y:y + h, x:x + w]

            hist = cv2.calcHist([roi_img], [0], None, [256], [0, 256])

            if hist[255] > area * self.text_roi_emptiness and (w > 4 and h > 4): # PARAM 10: 0.45 # rilevazione testo

                if (w > h * self.text_roi_proportion): # PARAM 11: 1.3 # proporzione testo self.roi_emptiness
                    cv2.rectangle(bw_copy, (x, y), (x + w - 1, y + h - 1), (0, 0, 0), -1)
                    cv2.rectangle(edges, (x, y), (x + w - 1, y + h - 1), (0, 0, 0), -1)
                    self._textBoxes.append(box)

        contours, hierarchy = cv2.findContours(bw_copy.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]

        boundingBoxes = sorted(boundingBoxes, key=lambda element: (element[1], element[0]))

        self._imageBoxes = []

        for i, box in enumerate(boundingBoxes):
            x, y, w, h = box

            area = w * h

            roi_img = bw_copy[y:y + h, x:x + w]

            hist = cv2.calcHist([roi_img], [0], None, [256], [0, 256])

            if hist[255] > area * self.image_roi_emptiness and (w > 4 and h > 4): # PARAM 12: 0.10 # rilevazione immagini
                # and (w > h * 1.3)

                if (h > w * self.vline_hw_proportion) and (w <= self.vline_w_maxsize): # PARAM 13, 14: 2, 10 # proporzione linee verticali
                    continue

                if (w > h * self.hline_wh_proportion) and (h <= self.hline_h_maxsize): # PARAM 15, 16: 2, 10 # proporzione linee orizzontali
                    continue

                font = cv2.FONT_HERSHEY_PLAIN
                # cv2.rectangle(original, (x, y), (x + w - 1, y + h - 1), (0, 255, 0), 1)
                cv2.rectangle(bw_copy, (x, y), (x + w - 1, y + h - 1), (0, 0, 0), -1)
                cv2.rectangle(edges, (x, y), (x + w - 1, y + h - 1), (0, 0, 0), -1)
                self._imageBoxes.append(box)


        contours, hierarchy = cv2.findContours(edges_ori.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]

        self._rectBoxes = []

        analyzed_points = []

        other_objects_found = copy.deepcopy(self._imageBoxes)
        other_objects_found.extend(self._textBoxes)

        for i, box in enumerate(boundingBoxes):
            x, y, w, h = box

            if (w < self.rect_w_minsize or h < self.rect_h_minsize): # PARAM 17, 18: 5, 5 # eliminazione rettangoloidi disturbo
                continue

            if (w >= self.rect_w_maxsize_01 and h >= self.rect_h_maxsize_01): # PARAM 19, 20: 800, 100 # eliminazione rettangoloidi disturbo
                continue

            if (w >= self.rect_w_maxsize_02 and h >= self.rect_h_maxsize_02): # PARAM 21, 22: 100, 800 # eliminazione rettangoloidi disturbo
                continue

            if (h > w * self.rect_hw_proportion) and (w <= self.rect_hw_w_maxsize): # PARAM 23, 24: 2, 10 # eliminazione rettangoloidi disturbo
                continue

            if (w > h * self.rect_wh_proportion) and (h <= self.rect_wh_h_maxsize): # PARAM 25, 26: 2, 10 # eliminazione rettangoloidi disturbo
                continue

            is_already_found = False

            for point_already_analyzed in analyzed_points:

                tolerance_region_w = self.hrect_proximity # PARAM 27: 10 # tolleranza vicinanza rettangoloidi
                tolerance_region_h = self.vrect_proximity # PARAM 28: 10 # tolleranza vicinanza rettangoloidi

                # tolerance_region = 20 * self._scaling_factor

                if (x >= point_already_analyzed[0] - tolerance_region_w and
                            x <= point_already_analyzed[0] + tolerance_region_w) and \
                        (y >= point_already_analyzed[1] - tolerance_region_h and
                                 y <= point_already_analyzed[1] + tolerance_region_h):
                    is_already_found = True
                    break

            if is_already_found == False:

                is_already_found_on_other = False

                for other_object in other_objects_found:
                    other_x, other_y, other_w, other_h = other_object

                    if x >= other_x and y >= other_y and w <= other_w and h <= other_h and other_h < self.vrect_others_proximity and other_w < self.hrect_others_proximity: # PARAM 29, 30: 40, 80 # tolleranza vicinanza altri candidati
                        is_already_found_on_other = True
                        break

                if is_already_found_on_other is False:
                    analyzed_points.append((x, y, w, h))
                    self._rectBoxes.append(box)

        for i, box in enumerate(self._imageBoxes):
            x, y, w, h = box
            if scaling_factor != 1:
                x *= scaling_factor
                x = int(x)
                y *= scaling_factor
                y = int(y)
                w *= scaling_factor
                w = int(w)
                h *= scaling_factor
                h = int(h)
            cv2.rectangle(self._debug_image, (x, y), (x + w - 1, y + h - 1), (255, 0, 0), 1)
            cv2.rectangle(self._i, (x, y), (x + w - 1, y + h - 1), 1, -1)
            cv2.rectangle(debug_i, (x, y), (x + w - 1, y + h - 1), 255, -1)

        for i, box in enumerate(self._rectBoxes):
            x, y, w, h = box
            if scaling_factor != 1:
                x *= scaling_factor
                x = int(x)
                y *= scaling_factor
                y = int(y)
                w *= scaling_factor
                w = int(w)
                h *= scaling_factor
                h = int(h)

            cv2.rectangle(self._debug_image, (x, y), (x + w - 1, y + h - 1), (0, 255, 0), 1)
            cv2.rectangle(self._r, (x-2, y-2), (x+w+2, y+h+2), 1, -1)
            cv2.rectangle(self._r, (x+2, y+2), (x+w-2, y+h-2), 0, -1)
            cv2.rectangle(debug_r, (x, y), (x + w - 1, y + h - 1), 255, -1)

        for i, box in enumerate(self._textBoxes):
            x, y, w, h = box
            if scaling_factor != 1:
                x *= scaling_factor
                x = int(x)
                y *= scaling_factor
                y = int(y)
                w *= scaling_factor
                w = int(w)
                h *= scaling_factor
                h = int(h)

            cv2.rectangle(self._debug_image, (x, y), (x + w - 1, y + h - 1), (0, 0, 255), 1)
            cv2.rectangle(self._t, (x, y), (x + w - 1, y + h - 1), 1, -1)
            cv2.rectangle(debug_t, (x, y), (x + w - 1, y + h - 1), 255, -1)

        self._debug_matrix = cv2.merge((debug_i, debug_r, debug_t))

        ret_img = cv2.merge((self._i, self._r, self._t))
        return ret_img

    def get_debug_matrix(self):
        return self._debug_matrix

    def get_debug_image(self):
        return self._debug_image

    def getImageBoxes(self, scaling_factor=1):
        image_boxes = []
        for box in self._imageBoxes:
            x, y, w, h = box
            x *= scaling_factor
            x = int(x)
            y *= scaling_factor
            y = int(y)
            w *= scaling_factor
            w = int(w)
            h *= scaling_factor
            h = int(h)
            image_boxes.append((x, y, w, h))
        return image_boxes

    def getRectBoxes(self, scaling_factor=1):
        rect_boxes = []
        for box in self._rectBoxes:
            x, y, w, h = box
            x *= scaling_factor
            x = int(x)
            y *= scaling_factor
            y = int(y)
            w *= scaling_factor
            w = int(w)
            h *= scaling_factor
            h = int(h)
            rect_boxes.append((x, y, w, h))
        return rect_boxes

    def getTextBoxes(self, scaling_factor=1):
        text_boxes = []
        for box in self._textBoxes:
            x, y, w, h = box
            x *= scaling_factor
            x = int(x)
            y *= scaling_factor
            y = int(y)
            w *= scaling_factor
            w = int(w)
            h *= scaling_factor
            h = int(h)
            text_boxes.append((x, y, w, h))
        return text_boxes
