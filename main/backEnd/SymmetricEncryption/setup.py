from setuptools import setup, Extension

setup(
    name='XorEncryption',
    ext_modules=[
        Extension(
            'XorEncryption',
            ['xorEncryptionClass.cpp'],
            include_dirs=[r'C:\Users\crook\AppData\Local\Programs\Python\Python312\Lib\site-packages\pybind11\include'],  
            extra_compile_args=['-std=c++17', '-march=generic'], 
        ),
    ],
    zip_safe=False,
)