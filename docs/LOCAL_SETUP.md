# SKYEYES Local Setup Guide

這份文件給接手專案的夥伴使用，目標是在本地端建立 SKYEYES，並能啟動 OpenCV 桌面版或 Web 介面版。

## 1. 取得專案

```powershell
git clone https://github.com/B11256002/SKYEYES.git
cd SKYEYES
```

如果要測試目前的 Web 介面版本，切到開發分支：

```powershell
git checkout codex/web-interface-test
```

## 2. 建立 Python 環境

建議使用 Python 3.10。

使用 conda：

```powershell
conda create -n skyeyes python=3.10
conda activate skyeyes
```

如果 PowerShell 無法執行 `conda activate`，可以先使用 Anaconda Prompt，或直接用環境裡的 Python 執行後續指令。

本機目前常用路徑範例：

```powershell
D:\Tool\Anaconda\envs\skyeyes\python.exe
```

## 3. 安裝套件

先安裝一般套件：

```powershell
pip install -r requirements.txt
```

如果要用 NVIDIA GPU，請確認安裝的是 CUDA 版 PyTorch。安裝後檢查：

```powershell
python tools\check_gpu.py
```

成功時應看到：

```text
CUDA available: True
```

如果沒有 GPU 或 CUDA 還不能用，把 `config.py` 改成：

```python
YOLO_DEVICE = "cpu"
```

## 4. 放置必要檔案

專案需要模型與測試影片：

```text
SKYEYES/
  models/
    best.pt
  videos/
    test.mp4
```

預設設定在 `config.py`：

```python
CAMERA_SOURCE = str(PROJECT_ROOT / "videos" / "test.mp4")
MODEL_PATH = str(PROJECT_ROOT / "models" / "best.pt")
```

如果檔名不同，請改 `config.py` 對應路徑。

## 5. 重要設定

常調整的設定都在 `config.py`：

```python
YOLO_DEVICE = "cuda"
YOLO_IMAGE_SIZE = 640
FRAME_WIDTH = 800
VISION_PROCESS_INTERVAL = 10
RUNTIME_TARGET_FPS = 10
WEB_STREAM_FPS = 10
WEB_JPEG_QUALITY = 70
VIDEO_REALTIME_PLAYBACK = True
```

說明：

- `YOLO_DEVICE`: `"cuda"` 使用 GPU，`"cpu"` 使用 CPU。
- `FRAME_WIDTH`: 影像顯示與辨識前的寬度，越小越省資源。
- `VISION_PROCESS_INTERVAL`: 每幾幀執行一次 YOLO、追蹤、邊界與警報判斷。
- `RUNTIME_TARGET_FPS`: 後端主迴圈目標 FPS。
- `WEB_STREAM_FPS`: Web 介面串流 FPS。
- `WEB_JPEG_QUALITY`: Web 串流 JPEG 品質，越低越省 CPU 與頻寬。

## 6. 啟動 OpenCV 桌面版

```powershell
python main.py
```

如果使用指定 Python：

```powershell
D:\Tool\Anaconda\envs\skyeyes\python.exe main.py
```

關閉方式：

```text
在 OpenCV 視窗按 q
```

## 7. 啟動 Web 介面版

Web 版會啟動 Flask 後端，並提供瀏覽器介面。

```powershell
python -m webapp.server
```

或使用指定 Python：

```powershell
D:\Tool\Anaconda\envs\skyeyes\python.exe -m webapp.server
```

啟動後打開瀏覽器：

```text
http://127.0.0.1:5000
```

停止後端：

```text
在執行中的 PowerShell 按 Ctrl + C
```

## 8. Web 介面切換影像來源

Web 介面右側有「影像來源」設定。

可選模式：

- `測試影片`: 使用 `config.py` 的 `CAMERA_SOURCE`。
- `Webcam`: 來源值填 `0`、`1`、`2` 等攝影機編號。
- `自訂來源`: 可填影片路徑或 OpenCV 可讀取的串流 URL。

範例：

```text
0
C:\Users\user\Desktop\test.mp4
http://192.168.4.1:81/stream
```

未來接 ESP32-S3-CAM 時，先確認它在 Windows 上是 Webcam 裝置、HTTP/MJPEG 串流，還是 COM port。前兩種目前可直接用 Web 介面測試；COM port 傳 JPEG 需要再新增 Serial 影像接收器。

## 9. 執行測試

```powershell
python -m unittest test_webapp.py test_display_dashboard.py test_aruco_landmark.py
```

完整測試可執行：

```powershell
python -m unittest
```

## 10. 常見問題

### CUDA 顯示不可用

先檢查目前執行的是不是正確環境：

```powershell
python tools\check_gpu.py
```

如果 `CUDA available: False`，代表目前 Python 裡的 PyTorch 不能使用 CUDA。可先改用：

```python
YOLO_DEVICE = "cpu"
```

### CPU 使用率太高

優先調低：

```python
RUNTIME_TARGET_FPS = 6
WEB_STREAM_FPS = 6
WEB_JPEG_QUALITY = 60
```

如果仍然太高，再降低：

```python
FRAME_WIDTH = 640
```

### Web 頁面開不起來

確認後端有啟動：

```powershell
python -m webapp.server
```

確認網址是：

```text
http://127.0.0.1:5000
```

如果 port 被占用，先關閉原本正在跑的後端 PowerShell，或按 `Ctrl + C` 停止。
