# Strokemaker

Strokemaker is a simple web-based tool that converts any uploaded image into a beautiful pencil sketch.

## 🚀 Live Demo
You can try the tool live here:  
👉 **[https://sarwesv.github.io/Strokemaker/](https://sarwesv.github.io/Strokemaker/)**

## ✨ Features
- Upload images in various formats (JPG, PNG, WEBP).
- Real-time conversion to pencil sketch using a "Color Dodge" blend.
- Download the resulting sketch as a PNG file.
- **Serverless**: Runs entirely in your browser using WebAssembly.

## 🛠️ Technologies Used
- **Python**: Core logic.
- **Streamlit**: User interface.
- **stlite**: For running Streamlit in the browser without a backend.
- **NumPy & Pillow**: For high-performance image processing.

## 💻 Repository
Source code: [https://github.com/sarwesv/Strokemaker](https://github.com/sarwesv/Strokemaker)

## 🚀 How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/sarwesv/Strokemaker.git
   cd Strokemaker
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
