
from mutagen import File
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
# Function to convert duration
# -----------------------------------------
def format_duration(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    return f"{minutes:02d}:{seconds:02d}"


# -----------------------------------------
# Main analyzer function
# -----------------------------------------
def analyze_audio(audio_path):

    supported_formats = {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".m4a",
        ".ogg",
        ".wma"
    }

    # Check file exists
    if not os.path.isfile(audio_path):
        print("Error: File does not exist.")
        return

    # Check extension
    extension = os.path.splitext(audio_path)[1].lower()

    if extension not in supported_formats:
        print("Error: Unsupported audio format.")
        print("Supported formats: MP3, WAV, FLAC, AAC, M4A, OGG, WMA")
        return

    try:
        # Read audio file
        audio = File(audio_path)

        if audio is None:
            print("Error: Unable to read audio file.")
            return

        # -----------------------------------------
        # Basic information
        # -----------------------------------------
        file_name = os.path.basename(audio_path)
        file_size = os.path.getsize(audio_path)

        # -----------------------------------------
        # Audio information
        # -----------------------------------------
        info = audio.info

        duration = getattr(info, "length", None)
        bitrate = getattr(info, "bitrate", None)
        channels = getattr(info, "channels", None)
        sample_rate = getattr(info, "sample_rate", None)

        # -----------------------------------------
        # Codec
        # -----------------------------------------
        codec = extension.upper().replace(".", "")

        # -----------------------------------------
        # Print report
        # -----------------------------------------
        print()
        print("================================")
        print("      AUDIO METADATA REPORT")
        print("================================")
        print()

        print(f"File Name       : {file_name}")
        print(f"File Size       : {format_file_size(file_size)}")
        print(f"File Format     : {codec}")

        print()

        print("AUDIO")
        print("--------------------------------")

        if duration is not None:
            print(f"Duration        : {format_duration(duration)}")
        else:
            print("Duration        : Not available")

        if bitrate is not None:
            print(f"Bit Rate        : {bitrate / 1000:.0f} kbps")
        else:
            print("Bit Rate        : Not available")

        if codec:
            print(f"Codec           : {codec}")
        else:
            print("Codec           : Not available")

        if channels is not None:
            print(f"Channels        : {channels}")
        else:
            print("Channels        : Not available")

        if sample_rate is not None:
            print(f"Sampling Rate   : {sample_rate} Hz")
        else:
            print("Sampling Rate   : Not available")

        # -----------------------------------------
        # Metadata
        # -----------------------------------------
        print()
        print("METADATA")
        print("--------------------------------")

        if audio.tags:
            for key, value in audio.tags.items():
                print(f"{key:<18}: {value}")
        else:
            print("No metadata available.")

        print()

    except Exception as e:
        print("Error: Unable to analyze audio.")
        print(f"Details: {e}")


# -----------------------------------------
# Program starts here
# -----------------------------------------
if __name__ == "__main__":

    audio_path = input("Enter audio path: ").strip()

    analyze_audio(audio_path)

