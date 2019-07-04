import setuptools

desc = "SnmpCollector python client"
setuptools.setup(
    name="pysnmpcollector",
    version="0.0.1",
    author="Steffen Schumacher",
    author_email="stsmr@vestas.com",
    description=desc,
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://github.com/steffenschumacher/pysnmpcollectorclient.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest', 'wheel', 'twine'
    ],
)
