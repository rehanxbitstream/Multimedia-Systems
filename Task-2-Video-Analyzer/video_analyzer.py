import os
import av

video_path = input("Enter video path: ").strip("\"'")

if not os.path.isfile(video_path):
    print("Error: File does not exist.")
    exit(1)

try:
    with av.open(video_path) as container:
        file_name = os.path.basename(video_path)
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Calculate duration safely
        duration_sec = float(container.duration) / av.time_base if container.duration else 0.0

        print("\n================================")
        print("      VIDEO METADATA REPORT     ")
        print("================================\n")
        print(f"File Name       : {file_name}")
        print(f"File Size       : {file_size_mb:.2f} MB")
        print(f"Container       : {container.format.name} ({container.format.long_name})")
        print(f"Duration        : {duration_sec:.2f}s ({int(duration_sec // 60)}m {duration_sec % 60:.1f}s)")
        print(f"Overall Bitrate : {container.bit_rate // 1000 if container.bit_rate else 'Unknown'} kbps\n")

        # --- Video Streams ---
        video_streams = [s for s in container.streams if s.type == "video"]
        if video_streams:
            for idx, stream in enumerate(video_streams):
                ctx = stream.codec_context
                
                # Safely convert frame rate fraction to float
                rate = stream.average_rate or stream.guessed_rate
                fps_str = f"{float(rate):.2f}" if rate and rate.denominator != 0 else "VFR/Unknown"

                # Frame count fallback
                frames = stream.frames if stream.frames > 0 else "N/A"

                print(f"VIDEO STREAM #{idx}")
                print("--------------------------------")
                print(f"Codec           : {ctx.name} ({ctx.codec.long_name})")
                print(f"Profile         : {ctx.profile or 'Unknown'}")
                print(f"Resolution      : {ctx.width}x{ctx.height}")
                print(f"Pixel Format    : {ctx.pix_fmt}")
                print(f"Framerate       : {fps_str} fps")
                print(f"Total Frames    : {frames}")
                print(f"Bitrate         : {ctx.bit_rate // 1000 if ctx.bit_rate else 'Unknown'} kbps\n")
        else:
            print("VIDEO: No video stream found.\n")

        # --- Audio Streams ---
        audio_streams = [s for s in container.streams if s.type == "audio"]
        if audio_streams:
            for idx, stream in enumerate(audio_streams):
                ctx = stream.codec_context
                lang = stream.metadata.get("language", "und")
                
                print(f"AUDIO STREAM #{idx} [{lang}]")
                print("--------------------------------")
                print(f"Codec           : {ctx.name} ({ctx.codec.long_name})")
                print(f"Channels        : {ctx.channels} ({ctx.layout.name if ctx.layout else 'Unknown'})")
                print(f"Sample Rate     : {ctx.sample_rate} Hz")
                print(f"Bitrate         : {ctx.bit_rate // 1000 if ctx.bit_rate else 'Unknown'} kbps\n")
        else:
            print("AUDIO: No audio stream found.\n")

except av.AVError as e:
    print(f"\nDecoding Error: {e}")
except Exception as e:
    print(f"\nUnexpected Error: {e}")
