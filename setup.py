from pathlib import Path

from setuptools import setup  # pyright: reportMissingTypeStubs=false

from startifact import __version__

readme_path = Path(__file__).parent / "README.md"

with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

classifiers = [
    "Environment :: Console",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Typing :: Typed",
]

if "a" in __version__:
    classifiers.append("Development Status :: 3 - Alpha")
elif "b" in __version__:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")

classifiers.sort()

setup(
    author="Cariad Eccleston",
    author_email="cariad@cariad.earth",
    classifiers=classifiers,
    description="Stages artifacts into Amazon Web Services",
    entry_points={
        "console_scripts": [
            "startifact=startifact.__main__:entry",
        ],
    },
    include_package_data=True,
    install_requires=[
        "ansiscape~=1.0",
        "asking~=1.0",
        "boto3~=1.20",
        "cline~=1.2",
        "semver~=2.13",
    ],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="startifact",
    packages=[
        "startifact",
        "startifact.exceptions",
        "startifact.parameters",
        "startifact.tasks",
    ],
    package_data={
        "startifact": ["py.typed"],
        "startifact.exceptions": ["py.typed"],
        "startifact.parameters": ["py.typed"],
        "startifact.tasks": ["py.typed"],
    },
    python_requires=">=3.8",
    url="https://github.com/cariad/startifact",
    version=__version__,
)
