from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vectormorph",
    version="0.1.0",
    author="Sohail Khan",
    author_email="your.email@example.com",  # replace with your email
    description="Intelligent image to SVG vectorization with AI-powered optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sohail000/vectormorph",
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
            "vectormorph=vectormorph.app:main",
        ],
    },
)