import setuptools

with open('__init__.py', 'r') as fh:
    lines = fh.readlines()
for line in lines:
    if line.startswith('__version__'):
        delim = '"' if '"' in line else "'"
        version = line.split(delim)[1]

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='wanglabpy',
    version=version,
    author='Yong Wang',
    author_email='yongwang@uark.edu',
    description='Python Tool Kit for Data Analysis Developed in Wang Lab',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://wang-lab.uark.edu',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)