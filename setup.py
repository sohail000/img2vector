from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="img2vector",
    version="1.1.2",  # Version bump for new features
    author="Sohail Khan",
    author_email="2013khansohail@gmail.com",
    description="Intelligent image to SVG vectorization with AI-powered optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sohail000/img2vector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "vtracer",
        "scikit-image",
        "opencv-python",
        "numpy",
        "pillow",
        "gradio>=3.0.0",
        "tqdm",  # For progress bars
    ],
    entry_points={
        "console_scripts": [
            "img2vector=img2vector.cli:main",  # Changed from app:main to cli:main
        ],
    },
)