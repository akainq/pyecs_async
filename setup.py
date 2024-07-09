from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension

extensions = [
   # Extension("pyecs_async.hibitset", ["pyecs_async/hibitsetsss/hibitset.pyx"]),
    Extension("pyecs_async.hibitset", ["pyecs_async/hibitset.pyx"],language="c++"),
]

setup(
    name='pyecs_async',
    packages=find_packages(),
    version='0.11.6.dev1',
    url='https://github.com/akainq/pyecs_async.git',
    license='MIT',
    author='AkaInq',
    author_email='aka.inq@gmail.com',
    description='Entity Component System Implementation for Python with Asyncio',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Topic :: Games/Entertainment',
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    ext_modules=cythonize(extensions),
)
