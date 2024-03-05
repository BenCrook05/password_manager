# information_manager
Password and information manager

# Project description
Password manager created for an A Level computer science project.
A key feature which the project aimed to solve was the limited ability to share passwords with live updates from current password managers. Since beginning the project, Apple has introduced this feature to keychain.
This project's main purpose was to demonstrate skills in a number of areas, hence the decision to use fewer libraries and implement more from scratch. 
The encryption is not current cryptographically secure as it uses small primes. Having said this, the implementation is all correct and increasing the length of the primes to 512 bits would represent proper RSA encryption. 

# Running the project
The modules created for encryption are compiled for AMD, but the setup files and raw cpp files are included which can be used to compile on any system using PyBind11.
