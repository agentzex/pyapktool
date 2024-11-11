import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="pyapktool",
    version="0.1",
    license="MIT",
    author="agentzex",
    author_email="cypy919@gmail.com",
    description="Unpack/Pack Android's apk and sign it",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agentzex/pyapktool",
    keywords=[
        "pyapktool",
        "apktool",
        "android apk",
        "apk decompiler",
        "apk decompile",
        "android app decompiler",
        "android app unpacker",
        "android app packer",
        "android apk unpacker",
        "android apk packer",
        "android app sign",
        "android apk sign",
        "android apk debug keys",
    ],
    platforms="any",
    install_requires=[
        "requests>=2.2.0"
    ],
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "pyapktool=pyapktool.pyapktool:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)

