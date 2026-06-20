"""
adb_draw_image.py
Usage:
  1) Connect phone with USB debugging enabled.
  2) Put the image you want to draw as 'input.png' in same folder.
  3) python adb_draw_image.py
Requirements:
  pip install opencv-python numpy pillow
  adb must be in PATH (or modify ADB_CMD variable below)
"""

import subprocess
import cv2
import numpy as np
import time
import sys
import os
from PIL import Image

ADB_CMD = r"C:\platform-tools\adb.exe"  # or full path like r"C:\platform-tools\adb.exe"

# ---------- Config (tweak these) ----------
IMG_PATH = "input.png"
CANVAS_PAD = 0.01   # portion of screen margin left around drawing (0..0.4)
TARGET_MAX_DIM_RATIO = 1  # how much of min(screen_w,screen_h) the drawing will use
SWIPE_DURATION_MS = 1  # duration of each small swipe in ms (increase for smoother but slower)
POINT_STEP = 10   # sample every N pixels along a contour (smaller -> smoother)
PAUSE_AFTER_STROKE = 0.00  # seconds between strokes
# ------------------------------------------

def run_adb(cmd_list):
    try:
        out = subprocess.check_output([ADB_CMD] + cmd_list, stderr=subprocess.STDOUT).decode().strip()
        return out
    except subprocess.CalledProcessError as e:
        print("ADB error:", e.output.decode(errors="ignore"))
        raise

def get_device_resolution():
    out = run_adb(["shell", "wm", "size"])
    # out example: "Physical size: 1080x2400" or "1080x2400"
    s = out.strip()
    if "Physical size:" in s:
        s = s.split("Physical size:")[-1].strip()
    if "x" in s:
        w,h = s.split("x")
        return int(w), int(h)
    raise RuntimeError("Couldn't parse device resolution from adb output: " + out)

def adb_swipe(x1,y1,x2,y2,duration_ms=SWIPE_DURATION_MS):
    cmd = ["shell", "input", "swipe", str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(int(duration_ms))]
    run_adb(cmd)

def preprocess_image(path, target_px):
    # Load with PIL for consistent handling of alpha
    im = Image.open(path).convert("RGBA")
    # Create white background for semi-transparent images
    bg = Image.new("RGBA", im.size, (255,255,255,255))
    bg.paste(im, (0,0), im)
    im = bg.convert("RGB")
    # Resize to target while keeping aspect ratio
    iw, ih = im.size
    scale = target_px / max(iw, ih)
    new_w, new_h = int(iw*scale), int(ih*scale)
    im = im.resize((new_w, new_h), Image.LANCZOS)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

def extract_contours_from_image(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # blur a bit
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    # Canny edges
    edges = cv2.Canny(blur, 30, 90)
    # find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Sort by length descending so larger shapes are drawn first
    contours = sorted(contours, key=lambda c: -len(c))
    return contours

def sample_contour_points(contour, step=POINT_STEP):
    pts = contour.reshape(-1,2)
    sampled = pts[::step]
    # ensure last point included
    if not np.array_equal(sampled[-1], pts[-1]):
        sampled = np.vstack([sampled, pts[-1]])
    return sampled.tolist()

def normalize_and_center_points(all_points, screen_w, screen_h):
    # all_points: list of lists of (x,y) in image coordinates
    # find bounding box in image coords
    xs = [p[0] for stroke in all_points for p in stroke]
    ys = [p[1] for stroke in all_points for p in stroke]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w_img = maxx - minx
    h_img = maxy - miny
    # target pixel size: allow padding on screen
    max_target = int(min(screen_w, screen_h) * TARGET_MAX_DIM_RATIO)
    scale = max_target / max(w_img, h_img) if max(w_img,h_img)>0 else 1.0
    # compute offset to center on screen
    draw_w = w_img * scale
    draw_h = h_img * scale
    pad_left = int(screen_w * CANVAS_PAD)
    pad_top = int(screen_h * CANVAS_PAD)
    start_x = pad_left + (screen_w - 2*pad_left - draw_w)/2
    start_y = pad_top  + (screen_h - 2*pad_top - draw_h)/2
    # Map points
    mapped = []
    for stroke in all_points:
        s2 = []
        for (x,y) in stroke:
            nx = ((x - minx) * scale) + start_x
            ny = ((y - miny) * scale) + start_y
            s2.append((nx, ny))
        mapped.append(s2)
    return mapped

def main():
    if not os.path.exists(IMG_PATH):
        print("Put the image you want to draw as 'input.png' in this folder.")
        return

    try:
        screen_w, screen_h = get_device_resolution()
    except Exception as e:
        print("Could not get device resolution. Ensure adb connected and authorized.")
        raise

    print(f"Device resolution detected: {screen_w} x {screen_h}")

    # Preprocess image - choose target pixel ~ 60% of device min dimension
    target_px = int(min(screen_w, screen_h) * TARGET_MAX_DIM_RATIO)
    cv_img = preprocess_image(IMG_PATH, target_px)

    contours = extract_contours_from_image(cv_img)
    if not contours:
        print("No contours found in image. Try higher-contrast image or different input.")
        return

    # Convert contours to list of strokes (sampled points)
    strokes = []
    for c in contours:
        pts = sample_contour_points(c, step=POINT_STEP)
        if len(pts) > 3:
            strokes.append(pts)

    # Map to screen coordinates
    mapped = normalize_and_center_points(strokes, screen_w, screen_h)

    print(f"Prepared {len(mapped)} strokes. Starting drawing in 3 seconds. Make sure drawing canvas is open on the phone.")
    time.sleep(3)

    try:
        
        # # Simple test: draw a single horizontal line
        # print("Testing single swipe...")
        # adb_swipe(100, 500, 400, 500, 200)
        # print("Swipe sent!")

        for i, stroke in enumerate(mapped):
            if len(stroke) < 2:
                continue
            # draw stroke by swiping between consecutive points in small segments
            for j in range(len(stroke)-1):
                x1,y1 = stroke[j]
                x2,y2 = stroke[j+1]
                adb_swipe(x1,y1,x2,y2, SWIPE_DURATION_MS)
                # tiny sleep to avoid overloading device
                time.sleep(0.001)
            time.sleep(PAUSE_AFTER_STROKE)
            print(f"Stroke {i+1}/{len(mapped)} drawn")
    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as e:
        print("Error during drawing:", str(e))
    print("Done.")

if __name__ == "__main__":
    main()

