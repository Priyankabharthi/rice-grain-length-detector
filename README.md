# Rice Grain Length Detector

Automated rice grain length measurement using computer vision. The project includes a **Python desktop app** (OpenCV + PyQt5) for analysis and a **React showcase website** for demos and documentation.


## Features

- Detect individual rice grains from an image
- Measure grain length in millimeters using a black reference strip (10 mm scale)
- Classify grains as Short, Medium, or Long (relative to max grain in sample)
- Visual output: original image, strip detection, and annotated grains
- React landing page with feature overview, demo video section, and screenshot gallery

## Project Structure

```
rice-grain-length-detector/
├── README.md
├── ricelengthdetector01-main/
│   ├── Python-main/
│   │   ├── main.py              # Desktop analyzer (PyQt5 GUI)
│   │   ├── requirements.txt     # Python dependencies
│   │   └── background1.jpg      # Optional splash background (place in this folder)
│   └── rice web/
│       └── web_interface/       # React + Vite showcase site
│           ├── package.json
│           └── src/
```

## How It Works

1. **Input image** — A single photo split vertically:
   - **Left half**: black reference strip (known 10 mm length for pixel-to-mm conversion)
   - **Right half**: rice grains on a light background
2. **Black strip detection** — Otsu thresholding, morphology, Canny edges, largest contour → strip length in pixels
3. **Grain detection** — Threshold, filter, morphology, contour filtering by area (2000–25000 px²)
4. **Measurement** — Rotated bounding box per grain; length in mm = `grain_pixels × (10 / strip_pixels)`
5. **Classification** — Short (&lt;30% of max), Medium (30–60%), Long (&gt;60% of max length in sample)

## Prerequisites

| Component | Requirements |
|-----------|--------------|
| Python app | Python 3.8+, pip |
| Web app | Node.js 18+, npm |

## Python Desktop App

### Install

```bash
cd ricelengthdetector01-main/Python-main
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

1. Click **Choose File** and select a `.jpg`, `.jpeg`, or `.png` image
2. Results appear in the left panel; processed views show on the right

### Image Tips

- Use consistent lighting and a plain light background for grains
- Keep the black reference strip clearly visible on the left
- Supported formats: JPG, JPEG, PNG
- If no black strip is detected, lengths are reported in **pixels** only (no mm conversion)

### Dependencies

- OpenCV (`opencv-python`)
- NumPy
- Matplotlib
- PyQt5

## Web Showcase

Marketing/demo site built with React, Vite, and Tailwind CSS.

### Install & run

```bash
cd "ricelengthdetector01-main/rice web/web_interface"
npm install
npm run dev
```

Open the URL shown in the terminal (usually `http://localhost:5173`).

### Build for production

```bash
npm run build
npm run preview
```

### Media assets

The web app expects media under `web_interface/assets/`:

| File | Used in |
|------|---------|
| `video_1.mp4` | Demo video section |
| `uiimage.png` | Screenshot gallery |
| `grainclassification.png` | Screenshot gallery |
| `outputimg.png` | Screenshot gallery |
| `imgaqui.jpg` | Screenshot gallery |
| `riceaqui.jpg` | About section |

These files are not included in the repository. Add your own screenshots and video to that folder before building, or the dev server will fail on missing imports.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-change`
3. Commit your changes
4. Push to your fork: `git push -u origin feature/your-change`
5. Open a Pull Request against `main`

## Known Limitations

- Threshold values (`185` for grains, Canny `120–300`) are tuned for specific lighting; other images may need parameter tweaks in `main.py`
- Grain area filter (`2000–25000` px²) may need adjustment for different resolutions
- Web contact form is display-only (no backend)
- Missing `assets/` and `background1.jpg` must be supplied locally


## Author

**Priyanka Bharti**
