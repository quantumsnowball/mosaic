from pathlib import Path

import click
import ffmpeg
import numpy as np

from mosaic.upscale.filter import upscale_filter
from mosaic.utils import VideoPathParamType


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def upscale(input_file: Path,
            output_file: Path,
            ) -> None:
    # extract first video stream info
    ffprobe_info = ffmpeg.probe(str(input_file))
    for stream in ffprobe_info['streams']:
        if stream['codec_type'] == 'video':
            width = int(stream['width'])
            height = int(stream['height'])
            framerate = str(stream['r_frame_rate'])
            frame_size = width * height * 3
            break
    else:
        raise ValueError("No video stream found.")

    # ffmpeg input and output procs
    in_proc = (
        ffmpeg
        .input(str(input_file))
        .output('pipe:',
                format='rawvideo',
                pix_fmt='rgb24')
        .global_args(
            '-hide_banner',
            '-loglevel', 'quiet')
        .run_async(pipe_stdout=True)
    )

    out_proc = (
        ffmpeg
        .output(
            ffmpeg.input('pipe:',
                         format='rawvideo',
                         pix_fmt='rgb24',
                         s=f'{width}x{height}',
                         framerate=framerate).video,
            ffmpeg.input(str(input_file)).audio,
            str(output_file),
            vcodec='libx264',
            pix_fmt='yuv420p')
        .global_args('-hide_banner')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    # conversion loop
    while True:
        in_bytes = in_proc.stdout.read(frame_size)
        if not in_bytes:
            break

        # Convert bytes to numpy array
        frame = np.frombuffer(in_bytes, np.uint8).reshape((height, width, 3))

        # apply a filter in python
        # TODO: do you upscaling magic here
        frame = upscale_filter(frame)

        # Convert back to bytes and send to ffmpeg output
        out_proc.stdin.write(frame.astype(np.uint8).tobytes())

    # Step 4: Cleanup
    in_proc.stdout.close()
    out_proc.stdin.close()
    in_proc.wait()
    out_proc.wait()
