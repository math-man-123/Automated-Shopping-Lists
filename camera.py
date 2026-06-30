from picamera2 import Picamera2
import cv2, time, printer


# global qr code detector
detector = cv2.QRCodeDetector()

# rasberry pi camera module
camera = Picamera2()

# configure and start the camera
config = camera.create_video_configuration(
    main={"format": "RGB888", "size": (1640,1232)},
    controls={"FrameRate": 30}
)
camera.configure(config); camera.start()

# warm-up time and alert user
time.sleep(0.3); printer.beep()


def scan_qrcode(
    scale: float = 0.3, sharpness: bool = False, 
    contrast: bool = False, debug: bool = False) -> str:
    """Capture a camera frame, apply some processing, detect qrcode."""

    # capture frame and always convert to grayscale
    frame = camera.capture_array("main")
    if debug: cv2.imwrite("img/frame.png", frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    if debug: cv2.imwrite("img/gray.png", frame)

    # always downscale to boost detection performance
    h, w = frame.shape
    size = (int(w * scale), int(h * scale))
    frame = cv2.resize(frame, size)
    if debug: cv2.imwrite("img/small.png", frame)

    # optional increase sharpness (boost contours)
    if sharpness:
        blur = cv2.GaussianBlur(frame, (0,0), 3)
        frame = cv2.addWeighted(frame, 1.5, blur, -0.5, 0)
        if debug: cv2.imwrite("img/sharpness.png", frame)

    # optional increase contrast (boost visibility)
    if contrast:
        frame = cv2.convertScaleAbs(frame, alpha=2, beta=0)
        if debug: cv2.imwrite("img/contrast.png", frame)

    # finds data, bounding box, and reconstructed qrcode
    try: data, bbox, qrcode = detector.detectAndDecode(frame)
    except Exception: return "" # dismiss detector errors

    # audio signal if data found
    if data: printer.beep()

    if debug and bbox is not None:
        # output final frame with bounding box
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        cv2.polylines(frame, [bbox.astype(int)], True, (0,255,0), 1)
        cv2.imwrite("img/bbox.png", frame)

    if debug and qrcode is not None:
        # output reconstructed qrcode from frame
        cv2.imwrite("img/qrcode.png", qrcode)

    return data
