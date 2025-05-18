import asyncio
from pathlib import Path

import aiofiles
from aiohttp import ClientSession
from yarl import URL

URLS = (
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth',
    'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth',
)


async def download(url_str: str,
                   session: ClientSession) -> None:
    url = URL(url_str)
    async with (
        session.get(url) as response,
        aiofiles.open(url.name, 'wb') as file
    ):
        data = await response.read()
        await file.write(data)
        print(f'Downloaded: {url.name}')


async def main():
    assert Path.cwd().name == 'state_dicts', 'Please run download script inside state_dicts/'

    async with ClientSession() as session:
        tasks = [download(url, session) for url in URLS]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
