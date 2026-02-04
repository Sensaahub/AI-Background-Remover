import streamlit as st
from PIL import Image, ImageFilter
from rembg import remove
import io
import time

st.set_page_config(
    page_title="AI Background Remover",
    layout="wide"
)

st.title("🖼️ AI Background Remover")
st.caption("Upload gambar → hapus background → download hasil")
st.divider()


st.sidebar.header("⚙️ Pengaturan")

fast_mode = st.sidebar.checkbox(
    "Fast Mode",
    value=False
)

bg_option = st.sidebar.selectbox(
    "Background hasil",
    ["Transparan", "Putih", "Abu-abu", "Biru", "Merah"]
)

st.sidebar.caption("Ukuran disarankan ≤ 5 MB")

col1, col2 = st.columns(2, gap="large")

def estimasi_waktu(image, fast_mode):
    w, h = image.size
    mp = (w * h) / 1_000_000
    return round((0.6 + mp * 0.4) if fast_mode else (1.8 + mp * 1.2), 1)

with col1:
    st.subheader("📤 Gambar Asli")

    uploaded_file = st.file_uploader(
        "Upload gambar (jpg / png)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGBA")
        image.thumbnail((1024, 1024))
        st.image(image, use_container_width=True)

        estimasi = estimasi_waktu(image, fast_mode)
        st.info(f"⏱️ Estimasi waktu: ± {estimasi} detik")

        process_btn = st.button(
            "🚀 Hapus Background",
            use_container_width=True
        )

with col2:
    st.subheader("✨ Hasil")

if uploaded_file and process_btn:
    with col2:
        progress = st.progress(0)
        status = st.empty()

        langkah = 20
        delay = estimasi / langkah

        for i in range(langkah):
            time.sleep(delay)
            progress.progress((i + 1) / langkah)
            status.text(f"Memproses... {int((i + 1) / langkah * 100)}%")

        if fast_mode:
            result = remove(image)
        else:
            result = remove(
                image,
                alpha_matting=True,
                alpha_matting_foreground_threshold=245,
                alpha_matting_background_threshold=5,
                alpha_matting_erode_size=3
            )
            result = result.filter(ImageFilter.GaussianBlur(radius=0.5))

        if bg_option != "Transparan":
            colors = {
                "Putih": (255, 255, 255, 255),
                "Abu-abu": (220, 220, 220, 255),
                "Biru": (30, 144, 255, 255),
                "Merah": (139, 0, 0, 255)
            }
            bg = Image.new("RGBA", result.size, colors[bg_option])
            result = Image.alpha_composite(bg, result)

        progress.empty()
        status.empty()

        st.image(result, use_container_width=True)

        buffer = io.BytesIO()
        result.save(buffer, format="PNG")

        st.download_button(
            "⬇️ Unduh PNG",
            buffer.getvalue(),
            file_name="no_background.png",
            mime="image/png"
        )
