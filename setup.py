import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bit_field',
    version='0.1.0',
    author="Arthur Gay",
    description="A bitfield diagram renderer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arth-ur/bitfield",
    packages=['bit_field'],
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
    keywords='bitfield bytefield diagram renderer svg',
    license='MIT',
    test_suite='nose.collector',
    tests_require=['nose'],
)
