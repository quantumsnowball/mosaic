from setuptools import setup

setup(
    name='mosaic',
    version='0.2.0',
    description='mosaic - handle mosaic in video',
    url='https://github.com/quantumsnowball/mosaic',
    author='Quantum Snowball',
    author_email='quantum.snowball@gmail.com',
    license='MIT',
    packages=['mosaic'],
    install_requires=[
        'click',
        'torch',
        'torchvision',
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'mosaic=mosaic.cli:mosaic',
        ]
    }
)
