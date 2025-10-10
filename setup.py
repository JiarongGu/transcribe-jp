from setuptools import setup, find_packages

setup(
    name='transcribe-jp',
    version='2.0.0',
    packages=find_packages(),
    py_modules=['transcribe_jp'],
    install_requires=[
        'openai-whisper>=20230314',
        'torch>=2.0.0',
        'numpy>=1.20.0',
        'anthropic>=0.3.0',  # Optional: for LLM features
    ],
    entry_points={
        'console_scripts': [
            'transcribe-jp=transcribe_jp:main',
        ],
    },
    python_requires='>=3.8',
    description='Transcribe Japanese audio/video files to VTT subtitle format with advanced hallucination filtering',
    long_description='A modular transcription tool using OpenAI Whisper with intelligent segmentation, hallucination detection, and optional LLM-powered text polishing.',
)
