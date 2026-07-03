# SKYEYES Handoff Notes

這份文件整理目前我協助完成的內容，以及其他人接手後要修改功能時應該看哪些檔案。

## 目前分支狀態

主要穩定版在：

```text
main
```

目前 Web 介面與 V1.0 候選功能在：

```text
codex/web-interface-test
```

已推送到 GitHub 的 Web 相關 commit：

```text
a180020 Add experimental web console
e1115a6 Add web video source switching
4a35080 Add runtime throttling and local setup guide
```

目前本機還有尚未推送的 V1.0 草稿改動：

- Web 系統設定顯示
- 警報 CSV 匯出
- 右側欄響應式整理
- CSV 匯出改成 Excel 可讀的 UTF-8 BOM

## 我協助完成的主要功能

### 1. OpenCV 桌面版 UI

相關檔案：

```text
main.py
ui/display.py
core/system_status.py
```

完成內容：

- 右側系統監控面板
- FPS、偵測數、界內數、地標數、追蹤數
- ESP32 狀態
- 穩定器狀態
- 最新警報
- 繁體中文介面文字

如果要修改 OpenCV 視窗上的文字、顏色、面板寬度，主要改：

```text
ui/display.py
```

如果要新增狀態欄位，通常要一起改：

```text
core/system_status.py
main.py
ui/display.py
```

### 2. Web 介面

相關檔案：

```text
webapp/server.py
webapp/runtime.py
webapp/static/index.html
webapp/static/styles.css
webapp/static/app.js
test_webapp.py
```

完成內容：

- Flask 後端
- MJPEG 影像串流
- Web 即時監控頁面
- FPS、偵測數、界內數、追蹤數、地標數、ESP32 狀態
- 最新警報
- 警報紀錄卷軸
- 警報 CSV 匯出
- 系統設定顯示
- 影像來源切換
- 響應式右側欄整理

如果要改頁面結構：

```text
webapp/static/index.html
```

如果要改樣式、排版、響應式：

```text
webapp/static/styles.css
```

如果要改前端資料更新、按鈕行為、分頁切換：

```text
webapp/static/app.js
```

如果要新增 API：

```text
webapp/server.py
```

如果要改影像處理流程：

```text
webapp/runtime.py
```

### 3. 影像來源切換

目前 Web 介面支援：

- 測試影片
- Webcam
- 自訂來源

相關檔案：

```text
webapp/runtime.py
webapp/server.py
webapp/static/index.html
webapp/static/app.js
```

後端 API：

```text
GET  /api/source
POST /api/source
```

如果未來要加入 ESP32-S3-CAM 專用模式，可以從這裡開始：

```text
webapp/runtime.py
```

新增一個 mode，例如：

```text
esp32_cam
```

然後在 `_build_source_config()` 裡把 COM port、HTTP stream、或 UVC webcam 轉成 OpenCV 可讀的 source。

### 4. 效能控制

相關檔案：

```text
config.py
camera/receiver.py
main.py
webapp/runtime.py
webapp/server.py
```

目前主要設定：

```python
VISION_PROCESS_INTERVAL = 10
RUNTIME_TARGET_FPS = 10
WEB_STREAM_FPS = 10
WEB_JPEG_QUALITY = 70
FRAME_WIDTH = 800
VIDEO_REALTIME_PLAYBACK = True
```

用途：

- `VISION_PROCESS_INTERVAL`: 每幾幀跑一次 YOLO、追蹤、邊界、ArUco、警報。
- `RUNTIME_TARGET_FPS`: 後端主迴圈目標 FPS。
- `WEB_STREAM_FPS`: Web 串流輸出 FPS。
- `WEB_JPEG_QUALITY`: MJPEG JPEG 品質。
- `FRAME_WIDTH`: 影像縮放寬度。

如果 CPU 太高，優先調：

```python
RUNTIME_TARGET_FPS = 6
WEB_STREAM_FPS = 6
WEB_JPEG_QUALITY = 60
FRAME_WIDTH = 640
```

如果辨識反應太慢，優先調：

```python
VISION_PROCESS_INTERVAL = 5
```

### 5. 警報紀錄與 CSV 匯出

相關檔案：

```text
alarm/manager.py
webapp/runtime.py
webapp/server.py
webapp/static/index.html
webapp/static/app.js
test_webapp.py
```

後端 API：

```text
GET /api/alarms
GET /api/alarms.csv
```

CSV 匯出目前使用：

```text
UTF-8 with BOM
```

這是為了讓 Windows Excel 直接開啟時中文不亂碼。

如果要修改 CSV 欄位，在這裡改：

```text
webapp/server.py
```

如果要改 Web 警報紀錄顯示方式，在這裡改：

```text
webapp/static/app.js
webapp/static/index.html
webapp/static/styles.css
```

### 6. ArUco 地標

相關檔案：

```text
landmark/aruco.py
tools/generate_aruco.py
assets/aruco/
config.py
test_aruco_landmark.py
```

目前設定：

```python
ARUCO_DICTIONARY = "DICT_4X4_50"
```

ArUco 不是任意圖案，必須使用指定 dictionary 裡的 marker。

產生 marker：

```powershell
python tools\generate_aruco.py --id 7 --size 800
```

如果要更換 ArUco dictionary，要同步確認：

```text
config.py
tools/generate_aruco.py
landmark/aruco.py
```

### 7. ESP32 通訊

相關檔案：

```text
communication/factory.py
communication/mock.py
communication/esp32.py
communication/protocol.py
core/esp32.py
config.py
test_esp32_communication.py
```

目前支援：

- ESP32 mock mode
- serial command protocol
- alarm command sending

目前設定：

```python
ESP32_ENABLED = False
ESP32_PORT = "COM3"
ESP32_BAUDRATE = 115200
```

如果沒有 ESP32，保持：

```python
ESP32_ENABLED = False
```

未來接 ESP32-S3-CAM 時要先確認它是哪種輸入：

- USB UVC webcam：Web 介面選 Webcam，來源填 `0`、`1`。
- HTTP/MJPEG stream：Web 介面選自訂來源，填 stream URL。
- USB Serial 傳 JPEG：需要新增 SerialCameraReceiver，目前尚未實作。

## 常見修改需求對照表

### 我要改模型檔路徑

改：

```text
config.py
```

設定：

```python
MODEL_PATH = str(PROJECT_ROOT / "models" / "best.pt")
```

### 我要改測試影片

改：

```text
config.py
```

設定：

```python
CAMERA_SOURCE = str(PROJECT_ROOT / "videos" / "test.mp4")
```

Web 介面也可以選「自訂來源」直接填影片路徑。

### 我要改邊界框

改：

```text
config.py
```

設定：

```python
BOUNDARY_POINTS = [
    (120, 120),
    (520, 120),
    (560, 420),
    (100, 420),
]
```

### 我要改警報冷卻時間

改：

```text
config.py
```

設定：

```python
ALARM_COOLDOWN_SECONDS = 2.0
```

### 我要改 Web 頁面右欄

改：

```text
webapp/static/index.html
webapp/static/styles.css
webapp/static/app.js
```

目前右欄使用：

- 系統狀態
- 健康狀態
- 控制分頁
- 最新警報
- 警報紀錄

如果新增內容太多，建議放進控制分頁，不要再一直往右欄垂直堆。

### 我要新增 Web API

改：

```text
webapp/server.py
```

如果 API 需要讀目前辨識狀態，通常也要改：

```text
webapp/runtime.py
```

並補測試：

```text
test_webapp.py
```

### 我要修改 YOLO 推論行為

改：

```text
detection/yolo.py
config.py
```

使用端也可能要改：

```text
main.py
webapp/runtime.py
```

## 測試方式

常用測試：

```powershell
python -m unittest test_webapp.py test_display_dashboard.py test_aruco_landmark.py
```

完整測試：

```powershell
python -m unittest
```

語法檢查：

```powershell
python -m py_compile main.py webapp\runtime.py webapp\server.py
```

## 啟動方式

OpenCV 桌面版：

```powershell
python main.py
```

Web 介面版：

```powershell
python -m webapp.server
```

瀏覽器打開：

```text
http://127.0.0.1:5000
```

如果使用本機指定 conda 環境：

```powershell
D:\Tool\Anaconda\envs\skyeyes\python.exe -m webapp.server
```

## 修改時的注意事項

- 不要把 `models/best.pt`、大型影片、暫存輸出推到 GitHub，除非專案明確需要。
- 改 Web 後端 API 時，記得補 `test_webapp.py`。
- 改畫面布局時，至少用 1280x720 測一次，避免右欄內容被擠掉。
- 改效能設定後，要同時觀察 CPU、GPU、FPS 和影片速度。
- 如果 `YOLO_DEVICE = "cuda"` 但 CUDA 不可用，會影響啟動；可先改成 `"cpu"` 測流程。
- ESP32-S3-CAM 接入前，先確認它在 Windows 上是 webcam、stream URL，還是 COM port。

## 建議下一步

V1.0 前建議優先完成：

- GPU 不可用時自動 fallback 到 CPU，並在 Web 顯示警告。
- 新增 `start_web.bat` 或 `run_web.py`，降低啟動門檻。
- 將 Web 介面功能 merge 回 main 或建立正式 release branch。
- 打 tag，例如 `v1.0.0`。
