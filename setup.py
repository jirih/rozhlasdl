from setuptools import setup, find_packages

setup(
    name='rozhlasdl',
    version='0.9.19',
    url='https://github.com/jirih/rozhlas-dl',
    packages=find_packages(),
    license='GPLv3',
    author='jirih',
    author_email='',
    description='Downloader for rozhlas.cz',
    long_description='Downloader for rozhlas.cz',
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'rozhlasdl = rozhlasdl.rozhlasdl:main'
        ]
    }, install_requires=[
        'html5lib', 'progressbar', 'retry'
    ],

)
