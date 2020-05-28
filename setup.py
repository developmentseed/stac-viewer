"""setup: stac-viewer"""

from setuptools import find_packages, setup

# Runtime requirements.
inst_reqs = ["rio-viz~=0.2.1", "requests"]

setup(
    name="stac-viewer",
    version="0.0.1",
    python_requires=">=3",
    description=u"Visualize STAC item in browser",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="STAC",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    install_requires=inst_reqs,
    entry_points="""
      [console_scripts]
      stac-viewer=stac_viewer.scripts.cli:viewer
      """,
)
