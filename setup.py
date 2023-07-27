from setuptools import setup, find_packages

setup(
    name="tangods_beamprofiler",
    version="0.0.1",
    description="Tango Device for calculating FWHM of a laser beam profile [µm] in two directions.",
    author="Daniel Schick",
    author_email="dschick@mbi-berlin.de",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["BeamProfiler = tangods_beamprofiler:main"]},
    license="MIT",
    packages=["tangods_beamprofiler"],
    install_requires=[
        "pytango",
        "numpy",
        "lmfit",
    ],
    url="https://github.com/MBI-Div-b/pytango-BeamProfiler",
    keywords=[
        "tango device",
        "tango",
        "pytango",
    ],
)
