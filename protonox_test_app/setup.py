from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


def read_requirements(filename: str) -> list[str]:
    requirements_path = Path(__file__).parent / filename
    requirements = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            requirements.append(cleaned)
    return requirements


setup(
    name="protonox",
    version="1.0",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "protonox=protonox_app.__main__:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
)