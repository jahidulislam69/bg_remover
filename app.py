import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
from streamlit_drawable_canvas import st_canvas
import io
import numpy as np

# Page settings
st.set_page_config(page_title="Background Remover", page_icon="🖼️")

# Initialize session state
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

st.title("🖼️ Background Remover App")
st.markdown("Upload an image and download the version with the background removed.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Load and fix image orientation
    input_image = Image.open(uploaded_file)
    input_image = ImageOps.exif_transpose(input_image)
    st.image(input_image, caption="Original Image", use_container_width=True)

    # Background removal
    with st.spinner("Removing background..."):
        img_bytes = io.BytesIO()
        input_image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        output_bytes = remove(img_bytes)
        output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    st.success("Background removed!")
    st.image(output_image, caption="Output Image", use_container_width=True)

    # Download original bg-removed image
    output_io = io.BytesIO()
    output_image.save(output_io, format="PNG")
    st.download_button(
        label="📥 Download Image",
        data=output_io.getvalue(),
        file_name="bg_removed.png",
        mime="image/png"
    )

    # Edit mode trigger
    if st.button("✏️ Edit & Erase More"):
        st.session_state.edit_mode = True

    if st.session_state.edit_mode:
        st.subheader("Mark the area to remove using the brush")

        # Brush customization (optional)
        brush_size = st.slider("Brush size", 5, 50, 15)

        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 1)",  # red
            stroke_width=brush_size,
            stroke_color="red",
            background_image=output_image,
            update_streamlit=True,
            height=output_image.height,
            width=output_image.width,
            drawing_mode="freedraw",
            key="canvas"
        )

        # Apply Erase
        if st.button("🧹 Apply Erase"):
            if canvas_result.image_data is not None:
                # Create mask from red drawing
                mask_np = np.array(canvas_result.image_data)[:, :, 0]
                mask = mask_np > 0

                # Apply transparency
                image_np = np.array(output_image)
                image_np[mask] = [0, 0, 0, 0]  # fully transparent
                cleaned_image = Image.fromarray(image_np)

                st.success("Marked areas removed!")
                st.image(cleaned_image, caption="Final Cleaned Image", use_container_width=True)

                # Download final cleaned image
                buf = io.BytesIO()
                cleaned_image.save(buf, format="PNG")
                st.download_button("📥 Download Cleaned Image", buf.getvalue(), "cleaned.png", "image/png")

        # Optional: cancel edit mode
        if st.button("🔙 Cancel Edit"):
            st.session_state.edit_mode = False
