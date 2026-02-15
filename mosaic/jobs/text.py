from pathlib import Path

from mosaic.jobs.job.base import Job
from mosaic.utils.ffprobe import FFprobe


def job_info(job: Job, i: int | None = None, *, verbose: bool = False) -> str:
    dim = 'dim ' if job.is_finished else ''
    width = 16
    indent = 2

    def r(txt: str) -> str:
        return f'[{dim}red]{txt}[/]'

    def g(txt: str) -> str:
        return f'[{dim}green]{txt}[/]'

    def y(txt: str) -> str:
        return f'[{dim}yellow]{txt}[/]'

    def b(txt: str) -> str:
        return f'[{dim}blue]{txt}[/]'

    def m(txt: str) -> str:
        return f'[{dim}magenta]{txt}[/]'

    def c(txt: str) -> str:
        return f'[{dim}cyan]{txt}[/]'

    def w(txt: str) -> str:
        return f'[{dim}white]{txt}[/]'

    def title() -> str:
        index = f'{i+1}. ' if i is not None else 'Job: '
        command = f'{job.command:8s}'
        info = f'{job.timestamp_pp} - {job.id}'
        return (
            w(index) + r(command) + g(info)
        )

    def progress() -> str:
        done = job.checklist.count_finished
        total = job.checklist.count

        name = f'{" "*indent + "progress":{width}s} '
        pct = f'{done / total:.2%}' if total > 0 else '0.00%'
        count = f'{done} / {total}'
        segment_time = f'{job.segment_time}'
        return (
            b(name) +
            r(pct) + w(', ') +
            y(count) + w(' done, ') +
            y(segment_time) + w(' each')
        )

    def video_file_details(file: Path, *, tag: str) -> str:
        txt = b(f'{" "*indent + tag:{width}s} ')
        if not file.exists():
            txt += w(f'{str(file)}, ') + y('not exist')
            return txt

        size_mb = round(file.stat().st_size / 1e6, 2)
        txt += w(f'{str(file)} ') + y(f'{size_mb:,.2f} MB')

        if not verbose:
            return txt

        details = FFprobe(file)
        for i, v_stream in enumerate(details.video):
            txt += (
                y(f'\n{" "*indent*2}v:{i} {v_stream.hms} ') +
                w(', ').join([c(f'{s}') for s in v_stream.summary])
            )
        for i, a_stream in enumerate(details.audio):
            txt += (
                m(f'\n{" "*indent*2}a:{i} {a_stream.hms} ') +
                w(', ').join([c(f'{s}') for s in a_stream.summary])
            )
        return txt

    def input_file() -> str:
        file = job.input_file
        return video_file_details(file, tag='input file')

    def output_file() -> str:
        file = job.output_file
        return video_file_details(file, tag='output file')

    rich_text = '\n'.join([
        title(),
        progress(),
        input_file(),
        output_file(),
    ])

    return rich_text
