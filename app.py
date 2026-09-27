import streamlit as st
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops
import io
import base64

# set_page_config MUST be the first Streamlit command
st.set_page_config(page_title="Strokemaker", layout="wide")

# Custom CSS for animations and UI cleanup
st.markdown("""
    <style>
    .stApp { animation: fadeIn 1.2s ease-in-out; }
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    [data-testid="stImage"] { animation: slideUp 0.8s ease-out; }
    @keyframes slideUp { 0% { transform: translateY(20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
    .stDownloadButton button {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.2) !important;
        width: 100% !important;
    }
    .stDownloadButton button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4) !important;
    }
    .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

def image_to_base64(image):
    # Resize for faster preview
    max_size = 1024
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size))
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def comparison_slider(img_before, img_after):
    b64_before = image_to_base64(img_before)
    b64_after = image_to_base64(img_after)
    
    # Dynamic height based on aspect ratio
    w, h = img_before.size
    aspect = w / h
    display_height = int(800 / aspect)
    display_height = min(max(display_height, 300), 1000)
    
    html_code = f"""
    <div id="canvas-container" style="position: relative; width: 100%; max-width: 800px; margin: auto; overflow: hidden; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); line-height: 0;">
        <img id="before-img" src="data:image/png;base64,{b64_before}" style="width: 100%; display: block;">
        <div id="after-image" style="position: absolute; top: 0; left: 0; width: 0%; height: 100%; overflow: hidden; border-right: 4px solid #333;">
            <img id="after-img-content" src="data:image/png;base64,{b64_after}" style="position: absolute; top: 0; left: 0; height: 100%; width: auto; max-width: none;">
        </div>
        <div id="drawing-tip" style="position: absolute; top: 0; left: 0%; width: 2px; height: 100%; background: #333; box-shadow: 0 0 15px rgba(0,0,0,0.5); pointer-events: none; opacity: 0;"></div>
    </div>
    <script>
        const container = document.getElementById('canvas-container');
        const afterImgDiv = document.getElementById('after-image');
        const afterImgContent = document.getElementById('after-img-content');
        const drawingTip = document.getElementById('drawing-tip');

        const resizeHandler = () => {{
            const containerWidth = container.offsetWidth;
            afterImgContent.style.width = containerWidth + 'px';
        }};

        window.addEventListener('resize', resizeHandler);
        
        setTimeout(() => {{
            resizeHandler();
            let pos = 0;
            const speed = 0.8; 
            drawingTip.style.opacity = "1";
            
            const animate = () => {{
                if (pos < 100) {{
                    pos += speed;
                    const val = Math.min(pos, 100) + '%';
                    afterImgDiv.style.width = val;
                    drawingTip.style.left = val;
                    requestAnimationFrame(animate);
                }} else {{
                    drawingTip.style.transition = "opacity 1s ease";
                    drawingTip.style.opacity = "0";
                    afterImgDiv.style.borderRight = "none";
                }}
            }};
            animate();
        }}, 300);
    </script>
    """
    st.components.v1.html(html_code, height=display_height + 20)

def dodge_blend(image, blur_radius):
    img_invert = ImageOps.invert(image)
    img_blur = img_invert.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    img_blur_invert = ImageOps.invert(img_blur)
    
    front = np.array(image, dtype=float)
    back = np.array(img_blur_invert, dtype=float)
    back[back == 0] = 1.0
    
    res = (front * 255.0) / back
    res = np.clip(res, 0, 255).astype(np.uint8)
    return Image.fromarray(res)

def pencil_sketch(input_image, weight, intensity, shadows):
    if input_image.mode in ("RGBA", "P"):
        background = Image.new("RGB", input_image.size, (255, 255, 255))
        background.paste(input_image, mask=input_image.split()[3] if input_image.mode == "RGBA" else None)
        input_image = background
    
    img_gray = ImageOps.grayscale(input_image)
    img_gray = img_gray.filter(ImageFilter.DETAIL)
    
    line_layer = dodge_blend(img_gray, blur_radius=weight)
    line_layer = ImageEnhance.Contrast(line_layer).enhance(intensity)
    
    shade_layer = dodge_blend(img_gray, blur_radius=25)
    
    final = ImageChops.multiply(line_layer, shade_layer)
    
    if shadows > 0:
        detail_layer = ImageEnhance.Contrast(img_gray).enhance(2.0)
        final = Image.blend(final.convert("RGB"), detail_layer.convert("RGB"), alpha=shadows)
    
    final = ImageEnhance.Contrast(final).enhance(1.2)
    final = ImageEnhance.Sharpness(final).enhance(1.5)
    
    return final

st.title("🎨 Strokemaker - Drawing Studio")
st.write("Watching your sketch come to life...")

# Sidebar for controls
with st.sidebar:
    st.header("✏️ Pencil Controls")
    weight = st.slider("Line Weight", 1, 10, 2)
    intensity = st.slider("Line Intensity", 1.0, 5.0, 2.5)
    shadows = st.slider("Shading Depth", 0.0, 0.5, 0.1)

uploaded_file = st.file_uploader("Upload an image (JPG, PNG, WEBP, BMP, TIFF, GIF)", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "gif"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    with st.spinner("Preparing drawing..."):
        sketch = pencil_sketch(image, weight, intensity, shadows)
        comparison_slider(image, sketch)

        # Download Section - properly indented
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            format_choice = st.selectbox("Format", ["PNG", "JPG", "PDF"])
        with col2:
            custom_name = st.text_input("Filename", "my_sketch")
        
        # Sanitization
        if not custom_name:
            custom_name = "sketch"
        
        buf = io.BytesIO()
        file_ext = format_choice.lower()
        mime = f"image/{file_ext}"
        
        if format_choice == "PDF":
            sketch.save(buf, format="PDF")
            mime = "application/pdf"
        elif format_choice == "JPG":
            sketch.convert("RGB").save(buf, format="JPEG")
            mime = "image/jpeg"
            file_ext = "jpg"
        else:
            sketch.save(buf, format="PNG")
            mime = "image/png"
        
        st.download_button(
            label=f"📥 Download .{format_choice}",
            data=buf.getvalue(),
            file_name=f"{custom_name}.{file_ext}",
            mime=mime,
            use_container_width=True
        )
