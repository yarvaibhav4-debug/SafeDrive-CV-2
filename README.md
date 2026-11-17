# SafeDrive CV

**Computer-vision-based lane marking analysis and traffic-light colour estimation for a driver-assistance prototype.**

SafeDrive CV is a third-year CSE academic prototype. It accepts a road video through a Flask web interface, processes its frames with OpenCV, estimates lane position from detected lane markings, analyses traffic-scene colours, and exports an annotated video with a rule-based safety message.

> **Safety notice:** This is an educational prototype, not a certified ADAS. It does not control a vehicle's steering, brakes, or acceleration. Do not use it for real-world driving decisions.

## Features

- Flask web interface for uploading road videos
- Video input support: MP4, AVI, MOV, and MKV
- Lane-processing pipeline using grayscale conversion, Gaussian blur, Canny edge detection, a region of interest, and probabilistic Hough line detection
- Approximate lane-centre estimation and lane status classification
- HSV-based red/yellow/green colour analysis in a selected image region
- Rule-based status messages: `STOP`, `CAUTION`, `GO`, `LANE DEPARTURE WARNING`, or `MONITOR ROAD`
- Annotated MP4 output with detected lane lines and status information

## How it works

```text
Road video upload
       |
       v
Flask application (app.py)
       |
       v
Frame extraction (OpenCV)
       |
       +---------------------------+
       |                           |
       v                           v
Lane detection                Colour analysis
Grayscale                     BGR -> HSV
Gaussian blur                 Upper-middle ROI
Canny edges                   Red / Yellow / Green masks
Region of interest
Hough line detection
       |                           |
       v                           v
Lane position/status          Estimated colour state
       |                           |
       +-------------+-------------+
                     |
                     v
              Rule-based status
                     |
                     v
           Annotated output video
```

## Technology stack

| Component | Technology |
|---|---|
| Web application | Python, Flask |
| Video processing | OpenCV |
| Numerical operations | NumPy |
| Upload filename handling | Werkzeug |
| Front end | HTML, CSS |

## Project structure

```text
SafeDrive-CV/
├── app.py                  # Flask routes and video upload workflow
├── video_processor.py      # Lane detection, colour analysis, video annotation
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── models/
│   └── README.txt          # Placeholder for a future model integration
├── static/
│   └── style.css           # Interface styling
└── templates/
    └── index.html          # Upload page and result display
```

## Run locally

### 1. Requirements

- Python 3.10 or newer
- pip
- A road video in MP4, AVI, MOV, or MKV format

### 2. Clone the repository

```bash
git clone https://github.com/<YOUR-USERNAME>/SafeDrive-CV.git
cd SafeDrive-CV
```

Replace `<YOUR-USERNAME>` with your GitHub username.

### 3. Create and activate a virtual environment

**Windows (PowerShell or Command Prompt):**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser, upload a road video, and select **Analyse Video**.

## Implementation details

### Lane detection

For each frame, the application:

1. Converts the frame from BGR to grayscale.
2. Applies Gaussian blur to reduce image noise.
3. Uses Canny edge detection to identify strong edges.
4. Masks the image to a trapezoidal road-region-of-interest.
5. Applies `HoughLinesP` to detect line segments.
6. Separates candidate left and right lane lines by slope, averages their parameters, and estimates the lane centre.
7. Classifies the lane position as `SAFE`, `SHIFTED LEFT`, `SHIFTED RIGHT`, or `LANE UNCERTAIN`.

### Traffic-light colour analysis

The current implementation converts each frame to HSV and counts red, yellow, and green pixels in an upper-middle region of the frame. The colour with the largest qualifying pixel count is returned as the estimated signal state; otherwise the result is `NOT DETECTED`.

**Important limitation:** this is colour-based scene analysis, not traffic-light object detection. It does not localise a traffic-light object with a trained detector. Red, yellow, or green objects elsewhere in the selected region can influence the estimate.

### Safety-message logic

The current rule-based logic prioritises the estimated colour state:

- Red → `STOP — RED SIGNAL`
- Yellow → `CAUTION — SLOW DOWN`
- Green → `GO`
- No recognised colour + shifted lane status → `LANE DEPARTURE WARNING`
- Otherwise → `MONITOR ROAD`

These are prototype display messages only and must not be interpreted as reliable driving instructions.

## Current limitations and future work

- Replace broad-region colour counting with traffic-light object localisation followed by colour classification inside the detected bounding box.
- Evaluate lane detection across different road types, lighting, weather, camera angles, and worn lane markings.
- Add temporal smoothing to reduce frame-to-frame status fluctuations.
- Add automated tests and performance evaluation on a labelled dataset.
- Improve handling of concurrent uploads and duplicate filenames.
- Consider browser-compatible video encoding for broader playback support.

The `models/` directory currently contains a placeholder README; no trained YOLO weights are included in this project.

## Suggested demonstration

For a clear classroom demonstration, use a short forward-facing road video with visible lane markings, stable daylight footage, and (if available) a traffic light. Upload it through the web page and explain the processing pipeline while showing the annotated output.

## Troubleshooting

**`python` is not recognized**

Install Python and enable the option to add Python to PATH, then reopen the terminal.

**`ModuleNotFoundError: No module named 'cv2'`**

Activate the virtual environment and run:

```bash
pip install -r requirements.txt
```

**The processed video does not play in the browser**

The application writes MP4 using OpenCV's `mp4v` codec. Browser support can vary. Try downloading the output and opening it in a local media player, or convert it with FFmpeg.

---

**Project type:** Academic implementation / computer vision prototype  
**Status:** Working prototype; further validation and model-based traffic-light detection are future improvements.
