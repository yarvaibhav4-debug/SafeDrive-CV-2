from flask import Flask, render_template, request, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename
from video_processor import process_video

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

ALLOWED = {".mp4", ".avi", ".mov", ".mkv"}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        f = request.files.get("video")
        if not f or not f.filename:
            error = "Please select a road video."
        else:
            ext = Path(f.filename).suffix.lower()
            if ext not in ALLOWED:
                error = "Use an MP4, AVI, MOV or MKV video."
            else:
                name = secure_filename(f.filename)
                input_path = UPLOADS / name
                f.save(input_path)
                output_name = f"processed_{Path(name).stem}.mp4"
                output_path = OUTPUTS / output_name
                try:
                    stats = process_video(str(input_path), str(output_path))
                    result = {"video": output_name, **stats}
                except Exception as exc:
                    error = f"Processing failed: {exc}"
    return render_template("index.html", result=result, error=error)

@app.route("/outputs/<path:name>")
def outputs(name):
    return send_from_directory(OUTPUTS, name)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
