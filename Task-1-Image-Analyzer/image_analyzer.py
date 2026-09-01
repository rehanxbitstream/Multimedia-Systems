
from PIL import Image, ExifTags
import os


# -----------------------------------------
# Function to convert file size
# -----------------------------------------
def format_file_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"


# -----------------------------------------
# Function to get EXIF metadata
# -----------------------------------------
def get_exif_metadata(image):
    exif_data = image.getexif()

    metadata = {}

    if not exif_data:
        return metadata

    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag_id, tag_id)

        # Ignore very large or unreadable metadata values
        if isinstance(value, bytes):
            continue

        metadata[tag_name] = value

    return metadata


# -----------------------------------------
# Main program
# -----------------------------------------
def analyze_image(image_path):

    supported_formats = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".webp",
        ".bmp"
    }

    # Check whether file exists
    if not os.path.isfile(image_path):
        print("Error: File does not exist.")
        return

    # Check file extension
    extension = os.path.splitext(image_path)[1].lower()

    if extension not in supported_formats:
        print("Error: Unsupported image format.")
        print("Supported formats: JPG, JPEG, PNG, TIFF, WEBP, BMP")
        return

    try:
        # Open image
        image = Image.open(image_path)

        # Basic information
        file_name = os.path.basename(image_path)
        file_size = os.path.getsize(image_path)
        file_format = image.format
        width, height = image.size
        color_mode = image.mode

        # DPI / resolution
        dpi = image.info.get("dpi")

        if dpi:
            resolution = f"{dpi[0]:.0f} x {dpi[1]:.0f} DPI"
        else:
            resolution = f"{width} x {height} pixels"

        # -----------------------------------------
        # Print report
        # -----------------------------------------
        print()
        print("================================")
        print("      IMAGE METADATA REPORT")
        print("================================")
        print()

        print(f"File Name       : {file_name}")
        print(f"File Size       : {format_file_size(file_size)}")
        print(f"File Format     : {file_format}")
        print(f"Width           : {width} pixels")
        print(f"Height          : {height} pixels")
        print(f"Resolution      : {resolution}")
        print(f"Color Mode      : {color_mode}")

        # -----------------------------------------
        # EXIF Metadata
        # -----------------------------------------
        print()
        print("EXIF Metadata")
        print("-------------------------------")

        exif = get_exif_metadata(image)

        if not exif:
            print("No EXIF metadata available.")
        else:
            # Camera
            camera = (
                exif.get("Model")
                or exif.get("Make")
                or "Not available"
            )

            # Date taken
            date_taken = (
                exif.get("DateTimeOriginal")
                or exif.get("DateTime")
                or "Not available"
            )

            # Orientation
            orientation = exif.get(
                "Orientation",
                "Not available"
            )

            print(f"Camera          : {camera}")
            print(f"Date Taken      : {date_taken}")
            print(f"Orientation     : {orientation}")

            # Print remaining EXIF metadata
            print()
            print("Other EXIF Metadata")
            print("-------------------------------")

            for key, value in exif.items():

                if key in [
                    "Model",
                    "Make",
                    "DateTimeOriginal",
                    "DateTime",
                    "Orientation"
                ]:
                    continue

                print(f"{key:<18}: {value}")

        print()

    except Exception as e:
        print(f"Error: Unable to analyze image.")
        print(f"Details: {e}")


# -----------------------------------------
# Program starts here
# -----------------------------------------
if __name__ == "__main__":

    image_path = input("Enter image path: ").strip()

    analyze_image(image_path)

