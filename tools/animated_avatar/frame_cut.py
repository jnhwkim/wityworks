import os
import cv2
from PIL import Image

def extract_and_resize_frames(video_path, output_dir, end_sec=2, target_size=(440, 440)):
    # Create the output directory.
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the video file.
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Unable to open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second (FPS).
    max_frame = int(fps * end_sec)   # Total frames within the requested duration.
    
    frame_count = 0
    saved_count = 0

    while cap.isOpened() and frame_count <= max_frame:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the OpenCV BGR image to a PIL RGB image.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Resize to the target dimensions with high-quality resampling.
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

        # Save as WebP (for example, frame_0000.webp, frame_0001.webp).
        output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.webp")
        img_resized.save(output_path, "WEBP", quality=90, method=6)
        
        saved_count += 1
        frame_count += 1

    cap.release()
    print(f"Done: saved {saved_count} frames as 440x440 WebP files to '{output_dir}'.")

# --- Script entry point ---
video_file = "092e130d-30b5-48a1-85eb-13273f0441b2.mp4" # Video file path.
output_folder = "output_frames"                        # Output directory name.

extract_and_resize_frames(video_file, output_folder, end_sec=2, target_size=(880, 880))
