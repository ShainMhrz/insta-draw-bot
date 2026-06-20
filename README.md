# 🎨 Insta-Draw Bot 

> An automated ADB script that turns your Android device into a high-speed digital tracing paper. 

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)]()
[![Platform](https://img.shields.io/badge/Platform-Android-green?logo=android&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ The Golden Rule: Pure Monochrome

**This bot does not "print" photographs; it traces geometry.** It has zero awareness of color, shading, or gradients. It will calculate the mathematical outlines of your image and draw 100% of the canvas using **whichever single brush color you manually have selected on your phone screen** when you hit Enter. 

***

## 🖼️ The "Holy Grail" Input Image

Because the bot uses **OpenCV Canny Edge Detection**, it looks for *sharp points of high contrast*. 

#### ✅ Feed it this (The Bot will love you):
* **"Coloring Book" vectors:** Clean, thick black line-art on a **100% pure white** (`#FFFFFF`) background.
* **Silhouettes:** High-contrast solid shapes, logos, or icons.
* **Typography:** Clean calligraphy, Kanji, or block lettering.

#### ❌ Do NOT feed it this (The Bot will make a cursed scribble):
* **Real-life selfies/photos:** It will try to draw every single eyelash, skin pore, and background shadow as a separate, jagged line.
* **Gradients:** Soft lighting transitions confuse the math into making 500 tiny overlapping micro-strokes.
* **Solid colored shapes:** If you give it a picture of a red apple, it will only draw the *outline* of the apple; it cannot "color it in".

***

## 📱 Device Compatibility

* **Supported:** Android Smartphones, Android Tablets, and Emulators (BlueStacks, LDPlayer).
* **Not Supported:** Apple iOS (iPhone / iPad). *This software relies entirely on the Android Debug Bridge (ADB) protocol.*

***

## ⚙️ Prerequisites

### 1. Computer Setup
1. Install **Python 3.7+**.
2. Download the official [Android Platform Tools (ADB)](https://developer.android.com/tools/releases/platform-tools) and extract it to a folder on your PC (e.g., `C:\platform-tools`).

### 2. Phone Setup
1. Go to **Settings** -> **About Phone**.
2. Tap **Build Number** 7 times to unlock *Developer Options*.
3. Go to **Settings** -> **Developer Options** and enable **USB Debugging**.
4. Connect the phone to your PC via USB. When the prompt appears on your phone screen, check *"Always allow from this computer"* and hit **OK**.

***

## 🚀 Installation 

1. **Clone the repo:**
   ```bash
   git clone https://github.com/ShainMhrz/insta-draw-bot.git
   cd insta-draw-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install opencv-python numpy pillow
   ```

3. **Tell the script where ADB lives:** Open `adb_draw_image.py` in your text editor and point the `ADB_CMD` variable to your downloaded `adb.exe`:

   ```python
   # Windows example:
   ADB_CMD = r"C:\platform-tools\adb.exe"

   # Mac / Linux example:
   ADB_CMD = "/usr/bin/adb"
   ```

***

## 🎨 How to Use

1. Place your target image inside the project folder.
2. Open `adb_draw_image.py` and assign the filename:
   ```python
   IMG_PATH = "my_vector_art.png" 
   ```
   ## Example image:
   <img width="600" height="900" alt="INPUT IMG" src="https://github.com/user-attachments/assets/8c183699-d4a3-4e60-9d78-ba720118c16c" />


3. Open your mobile canvas (Instagram Story, Snapchat, Sketchbook, Notes) and **select your brush tool & brush color.**
4. Run the script:
   ```bash
   python adb_draw_image.py
   ```
5. **The 3-Second Scramble:** The terminal will start a 3-second countdown. Immediately click your mouse back over to your phone screen/emulator so the OS registers the touch inputs to the right window!

***

## OUTPUT: 
<img width="450" height="800" alt="OUTPURT IMG" src="https://github.com/user-attachments/assets/85628a7a-ab8d-442b-ab70-c0136b099a5c" />

## 🧠 Pro-Dev Tips for the best result

### 1. The "Hollow Track" quirk (And how to beat it)
When you feed OpenCV a thick black line, it registers an edge when the white turns to black, and *another* edge when the black turns back to white. **The bot will draw every thick line twice as a parallel track.** * **The Fix:** Set your digital mobile brush size to roughly **15%–20% thickness**. When the bot draws the left rail and the right rail, the digital ink will bleed together in the middle, fusing it into one gorgeous, solid comic stroke.

### 2. Fine-Tuning the Engine
Open the top of `adb_draw_image.py` to change the physics of the bot:

| Variable | Default | What happens if you change it? |
| :--- | :--- | :--- |
| `POINT_STEP` | `10` | **The Detail knob.** Set to `5` for hyper-accurate tracing (takes 4x longer). Set to `20` for a super-fast, low-poly sketch. |
| `SWIPE_DURATION_MS` | `1` | **The CPU bottleneck knob.** If your phone is drawing broken, dotted lines, your phone's processor can't catch the USB packets fast enough. Raise to `2` or `3`. |
| `CANVAS_PAD` | `0.01` | **The Safety Margin.** Keeps the bot 1% away from the edges of your screen so it doesn't accidentally hit the "Back" or "X" UI buttons. |

***
