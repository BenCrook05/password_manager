#include <iostream>
#include <string>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cstdlib>
#include <ctime>
namespace py = pybind11;

class XorEncryption{
    public:
    std::string GenerateKeys(int length){
        srand(static_cast<unsigned int>(time(nullptr)));  // need to reset random seed so that key is different every time
        std::string key = "";
        for(int i = 0; i < length; i++){
            char random_char = static_cast<char>((rand() % 10) + '0');
            std::string char_as_string(1, random_char);
            key += char_as_string;
            }
        return key;
    };

    std::string encryptdecrypt(std::string message, std::string key){
        std::string encryptedMessage = "";
        std::string unicodeString = "";
        for (char i : message){
            unicodeString += static_cast<unsigned char>(i);
        }
        // edit key length to match message length
        while (key.length() < unicodeString.length()){
            key += key;
        }
        for (int i = 0; i < unicodeString.length(); i++){
            encryptedMessage += unicodeString[i] ^ key[i];
        }
        return encryptedMessage;
    }

};


PYBIND11_MODULE(XorEncryption, m) {
    py::class_<XorEncryption>(m, "XorEncryption")
        .def(py::init<>())
        .def("encryptdecrypt", &XorEncryption::encryptdecrypt)
        .def("generate_key", &XorEncryption::GenerateKeys);
}
