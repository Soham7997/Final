---

## 🚀 Installation Guide

### Prerequisites
* **OS:** Windows 10/11 (Architecture optimized for Windows)
* **Python:** Anaconda or Miniconda installed
* **Git:** Version control installed

### 1. Clone the Repository
```bash
git clone [https://github.com/Soham7997/Final.git](https://github.com/Soham7997/Final.git)
cd Final
```

2. Create the "Golden" Environment
We use a specific environment configuration to ensure MediaPipe, OpenCV, and NumPy work together without conflict.

```bash
# Create a clean Python 3.11 environment
conda create -n body_tracking python=3.11 -y

# Activate the environment
conda activate body_tracking
```

3. Install Dependencies
Run this exact command to prevent version conflicts (Dependency Hell):
```bash
pip install -r requirements.txt
```
(Note: This installs the stable "Golden Stack": NumPy < 2.0, MediaPipe 0.10.21, and OpenCV < 4.10)

⚡ How to Run
On Windows: Double-click start_all.bat OR run in terminal:

If you need to see logs for each server separately, open two terminal windows:

Terminal 1 (Main Website):
```bash
conda activate body_tracking
python server.py
```

Terminal 2 (Body AI Model):
```bash
conda activate body_tracking
python run_dev.py
```

🎮 Usage Guide
Open your browser and go to: http://localhost:5000

Login to the dashboard.
Choose a Module:
Object Detection: Runs on Port 5000.
Gender Detection: Runs on Port 5000.
Body Tracking: When you click this, the system automatically redirects you to the high-performance node at http://localhost:8000.

🔧 Troubleshooting
"MediaPipe not available" / Missing 'solutions' module:
Ensure you are using Python 3.11 (not 3.13).
Ensure you installed mediapipe==0.10.21.
Ensure you have the Visual C++ Redistributables installed.
"Address already in use" error:
Another program is using Port 5000 or 8000.
Fix: Close other python windows or run taskkill /F /IM python.exe in the terminal to kill old processes.

📦 Tech Stack
Backend: Flask (Web), FastAPI (AI Service)
AI/ML: MediaPipe, YOLOv8, PyTorch
Computer Vision: OpenCV
Frontend: HTML5, CSS3, JavaScript
