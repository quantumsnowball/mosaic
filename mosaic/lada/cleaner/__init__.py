import os
from contextlib import ExitStack
from pathlib import Path
from typing import Self

import mosaic.lada.cleaner.lib.audio_utils as audio_utils
import mosaic.lada.cleaner.utils as utils
from mosaic.lada.cleaner.lib.frame_restorer import FrameRestorer, load_models
from mosaic.lada.cleaner.lib.video_utils import (VideoWriter,
                                                 get_video_meta_data)
from mosaic.utils import TEMP_DIR
from mosaic.utils.logging import trace
from mosaic.utils.spec import VideoSource
from mosaic.utils.time import HMS


class Cleaner:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None,
        end_time: HMS | None,
        output_file: Path,
        raw_info: bool,
    ) -> None:
        source = VideoSource(input_file, start_time, end_time)
        self.cm = ExitStack()

    @trace
    def __enter__(self) -> Self:
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        self.wait()
        self.cm.close()

    @trace
    def start(self) -> None:
        # vars
        device = 'cuda:0'
        mosaic_restoration_model_name = 'basicvsrpp'

        mosaic_detection_model, mosaic_restoration_model, preferred_pad_mode = load_models(
            device,
            mosaic_restoration_model,
            mosaic_restoration_model_path,
            mosaic_restoration_config_path,
            mosaic_detection_model_path
        )

        video_metadata = get_video_meta_data(input_path)

        frame_restorer = FrameRestorer(device, input_path, max_clip_length, mosaic_restoration_model_name,
                                       mosaic_detection_model, mosaic_restoration_model, preferred_pad_mode)
        success = True
        # video_tmp_file_output_path = os.path.join(tempfile.gettempdir(
        # ), f"{os.path.basename(os.path.splitext(output_path)[0])}.tmp{os.path.splitext(output_path)[1]}")
        # Path(output_path).parent.mkdir(exist_ok=True, parents=True)
        video_tmp_file_output_path = TEMP_DIR / 
        try:
            frame_restorer.start()

            with VideoWriter(
                video_tmp_file_output_path,
                video_metadata.video_width,
                video_metadata.video_height,
                video_metadata.video_fps_exact,
                codec='h264',
                crf=None,
                moov_front=False,
                time_base=video_metadata.time_base,
                preset=None,
                custom_encoder_options=""
            ) as video_writer:
                frame_restorer_progressbar = utils.Progressbar(video_metadata, frame_restorer)
                for elem in frame_restorer_progressbar:
                    if elem is None:
                        success = False
                        print("Error on export: frame restorer stopped prematurely")
                        break
                    (restored_frame, restored_frame_pts) = elem
                    video_writer.write(restored_frame, restored_frame_pts, bgr2rgb=True)
                    frame_restorer_progressbar.update()
                    frame_restorer_progressbar.update_time_remaining_and_speed()
        except (Exception, KeyboardInterrupt) as e:
            success = False
            if isinstance(e, KeyboardInterrupt):
                raise e
            else:
                print("Error on export", e)
        finally:
            frame_restorer.stop()

        if success:
            print("Processing audio")
            audio_utils.combine_audio_video_files(video_metadata, video_tmp_file_output_path, output_path)
        else:
            if os.path.exists(video_tmp_file_output_path):
                os.remove(video_tmp_file_output_path)

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        print('wait for other workers')

    @trace
    def stop(self) -> None:
        print('stop other workers')
