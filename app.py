# Import required libraries
import qrcode                 # Library to generate QR codes
import gradio as gr            # Gradio for building the web interface
from PIL import Image          # Pillow for image processing
import os                      # OS utilities (not strictly required here, but commonly used)
import uuid                    # Used to generate unique filenames


def rgba_to_rgb(color_str):
    """
    Convert color values coming from Gradio into a format
    compatible with the qrcode library.

    Gradio may return colors as:
    - Hex string (#RRGGBB)
    - RGBA string (rgba(r,g,b,a))

    This function converts RGBA to RGB.
    """
    # If color is already in hex format, return as-is
    if color_str.startswith("#"):
        return color_str

    # If color is in RGBA format, extract R, G, B values
    if color_str.startswith("rgba"):
        parts = color_str[5:-1].split(",")
        r, g, b = [int(float(p.strip())) for p in parts[:3]]
        return (r, g, b)

    # Fallback: return the original value
    return color_str


def generate_qr_code(text, fill_color, back_color, logo_file):
    """
    Generate a QR code with custom colors and an optional logo.

    Parameters:
    - text: Text or URL to encode in the QR code
    - fill_color: QR foreground color
    - back_color: QR background color
    - logo_file: Optional uploaded logo file

    Returns:
    - PIL Image for preview
    - File path for downloading the QR code
    """

    # If no text is provided, return empty outputs
    if not text:
        return None, None

    # Convert colors into QR-compatible format
    fill_color = rgba_to_rgb(fill_color)
    back_color = rgba_to_rgb(back_color)

    # Create a QRCode object with high error correction
    qr = qrcode.QRCode(
        version=1,                                      # Size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction (good for logos)
        box_size=10,                                   # Size of each QR box
        border=4,                                      # Border thickness
    )

    # Add text data to the QR code
    qr.add_data(text)
    qr.make(fit=True)

    # Generate the QR image and convert it to RGB
    img = qr.make_image(
        fill_color=fill_color,
        back_color=back_color
    ).convert("RGB")

    # If a logo file is provided, add it to the center of the QR code
    if logo_file:
        # Open logo image with transparency
        logo = Image.open(logo_file.name).convert("RGBA")

        # Get QR image dimensions
        img_w, img_h = img.size

        # Resize logo to be smaller than the QR code
        factor = 4
        logo_size = (img_w // factor, img_h // factor)
        logo = logo.resize(logo_size)

        # Calculate position to center the logo
        pos = (
            (img_w - logo_size[0]) // 2,
            (img_h - logo_size[1]) // 2
        )

        # Paste logo onto QR code using transparency mask
        img.paste(logo, pos, mask=logo)

    # Save QR code to a temporary file for download
    tmp_filename = f"/tmp/qr_code_{uuid.uuid4().hex}.png"
    img.save(tmp_filename)

    # Return both the preview image and file path
    return img, tmp_filename


# -------------------- Gradio Interface --------------------

iface = gr.Interface(
    fn=generate_qr_code,    # Function to call when inputs change
    inputs=[
        gr.Textbox(label="Enter text or URL"),
        gr.ColorPicker(label="QR code color", value="#000000"),
        gr.ColorPicker(label="Background color", value="#ffffff"),
        gr.File(label="Optional logo (PNG with transparency)")
    ],
    outputs=[
        gr.Image(type="pil", label="QR Code Preview"),
        gr.File(label="Download QR Code")
    ],
    title="Custom QR Code Generator",
    description=(
        "Generate QR codes with custom colors, optional logo, "
        "preview them, and download as PNG."
    )
)

# Launch the Gradio web app
if __name__ == "__main__":
    iface.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
