import time

from ultralytics import YOLO

from core.detection import Detection


class YOLODetector:

    def __init__(self, model_path, confidence=0.4):

        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            verbose=False
        )

        detections = []

        result = results[0]

        # 若沒有 OBB 偵測結果
        if result.obb is None:
            return detections

        obb = result.obb

        corners_list = obb.xyxyxyxy.cpu().numpy()
        classes = obb.cls.cpu().numpy()
        scores = obb.conf.cpu().numpy()

        for corners, cls_id, score in zip(corners_list, classes, scores):

            # 四個角點
            points = [(int(x), int(y)) for x, y in corners]

            # 中心點
            center_x = int(sum(p[0] for p in points) / 4)
            center_y = int(sum(p[1] for p in points) / 4)

            detection = Detection(
                label=result.names[int(cls_id)],
                confidence=float(score),
                corners=points,
                center=(center_x, center_y),
                timestamp=time.time()
            )

            detections.append(detection)

        return detections