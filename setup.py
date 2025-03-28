from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="img2vector",
    version="1.0.2",
    author="Sohail Khan",
    author_email="2013khansohail@gmail.com",  # replace with your email
    description="Intelligent image to SVG vectorization with AI-powered optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sohail000/img2vector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "vtracer",
        "scikit-image",
        "opencv-python",
        "numpy",
        "pillow",
        "gradio>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "img2vector=img2vector.app:main",
        ],
    },
)