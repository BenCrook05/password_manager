from setuptools import setup, Extension

setup(
    name='RSAasyncEncryption',
    ext_modules=[
        Extension(
            'RSAEncryption',
            ['asyncClass.cpp'],
            include_dirs=[r'C:\Users\crook\AppData\Local\Programs\Python\Python312\Lib\site-packages\pybind11\include'],
            extra_compile_args=['-std=c++17', '-march=generic'], # generic architecture flag
        ),
    ],
    zip_safe=False,
)
