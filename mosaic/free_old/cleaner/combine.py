from pathlib import Path

from mosaic.free_old.utils import ffmpeg


def combine_result_to_video(fps,
                            temp_dir: Path,
                            output_file: Path) -> None:
    ffmpeg.image2video(fps,
                       temp_dir/'replace_mosaic/output_%06d.jpg',
                       temp_dir/'voice_tmp.mp3',
                       output_file)
