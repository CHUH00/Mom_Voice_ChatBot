import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, target_sr=16000): 
        self.target_sr = target_sr

    def preprocess(self, input_path: str, output_path: str) -> bool:
        """
        Normalize audio using ffmpeg:
        - Convert to mono
        - Resample to target sample rate (default 16kHz)
        """
        try:
            command = [
                "ffmpeg",
                "-y",              # overwrite output
                "-i", input_path,  # input file
                "-ac", "1",        # mono
                "-ar", str(self.target_sr), # target sample rate
                output_path
            ]
            # Run without showing output unless there's an error
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Successfully processed audio: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to process audio {input_path} with ffmpeg: {e}")
            return False

    def validate_audio(self, file_path: str) -> bool:
        """Simple check if ffmpeg can format/read it"""
        try:
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            duration = float(result.stdout.strip())
            return duration > 0
        except Exception as e:
            logger.error(f"Invalid audio file {file_path}: {e}")
            return False
