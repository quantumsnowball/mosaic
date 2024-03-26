import subprocess
from pathlib import Path
from typing import Sequence

from alive_progress import alive_bar


def ffmpeg(args: Sequence[str],
           *,
           exp_total_secs: int,
           stats_period: float = 0.1):
    # verify args
    args = list(map(str, args))
    args = list(filter(lambda x: len(x) > 0, args))
    # create ffmpeg command
    cmd = ['ffmpeg']
    cmd += ['-loglevel', 'fatal']
    cmd += ['-progress', 'pipe:1']
    cmd += ['-stats_period', str(stats_period)]
    cmd += args

    # run ffmpeg in a process, monitor stdout
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if proc.stdout is not None:
        # display a progress bar
        with alive_bar(exp_total_secs) as bar:
            for line_b in proc.stdout:
                line = line_b.decode().strip()
                # track ffmpeg rendering speed
                if line.startswith('speed='):
                    speed_text = line.split('=', maxsplit=1)[1]
                    speed = float(speed_text.replace('x', ''))
                    progress = speed * 0.1
                    bar.text(speed_text)
                    bar(progress)

            # finish bar to 100%
            bar(exp_total_secs-bar.current)
    # join
    proc.wait()


if __name__ == '__main__':
    ffmpeg(f' -i {Path.home()}/Videos/input.mp4'
           ' -ss 00:00:00 -to 00:10:00'
           ' -vf scale=640:480'
           ' -y'
           f' {Path.home()}/Videos/output-640x480.mp4'.split(' '),
           exp_total_secs=10*60)
