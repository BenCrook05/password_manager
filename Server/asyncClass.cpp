#include <iostream>
#include <ctime>
#include <time.h>
#include <stdlib.h>
#include <map>
#include <string>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace std;


class KeyGeneration{
public:
    unsigned long long int encrypt(unsigned long long int m, unsigned long long int e, unsigned long long int n){
        return modPow(e, m, n);
    }

    unsigned long long int decrypt(unsigned long long int c, unsigned long long int d, unsigned long long int n){
        return modPow(d, c, n);
    }

    py::tuple generateKeys(){
        unsigned long long int p, q, e, d, n, maxD;

        do {
            pair<unsigned long long int, unsigned long long int> pq = getpq();
            p = pq.first;
            q = pq.second;
            unsigned long long int totient = eulerTotient(p, q);
            e = gete(totient);
            d = modInverse(e, totient);
            n = p * q;
            maxD = n - 1;
        } while (d == -1 || d > maxD);

        return py::make_tuple(e, d, n);
    }


private:
    unsigned long long int gcd(unsigned long long int a, unsigned long long int b){
        if (b == 0){
            return a;
        } else {
            return gcd(b, a % b);
        }
    }

    unsigned long long int lcm(unsigned long long int a, unsigned long long int b){
        return (a / gcd(a, b)) * b;
    }

    bool isPrime(unsigned long long int n){
        if (n < 2 || (!(n & 1) && n != 2)){
            return false;
        }
        for (unsigned long long int i = 3; i * i <= n; i += 2){
            if (n % i == 0){
                return false;
            }
        } 
        return true;    
    }

    // Key Generation
    pair<unsigned long long int, unsigned long long int> getpq(){
        // get two primes
        srand(static_cast<unsigned int>(time(nullptr)));
        unsigned long long int p = rand() % static_cast<unsigned long long int>(pow(2, 10));
        while (!isPrime(p) || p < 200 || p > 800){
            p = rand() % static_cast<unsigned long long int>(pow(2, 10));
        }
        unsigned long long int q = rand() % static_cast<unsigned long long int>(pow(2, 10));
        while (!isPrime(q) || q < 200 || q > 800){
            q = rand() % static_cast<unsigned long long int>(pow(2, 10));
        }
        return make_pair(p, q);
    }

    unsigned long long int eulerTotient(unsigned long long int p, unsigned long long int q){
        return lcm(p - 1, q - 1);
    }

    bool isCoprime(unsigned long long int a, unsigned long long int b){
        return gcd(a, b) == 1;
    }

    unsigned long long int gete(unsigned long long int totient){
        unsigned long long int e = static_cast<unsigned long long int>(pow(2, 16)) + 1;
        while (!isCoprime(e, totient)){
            e++;
        }
        return e;
    }

    unsigned long long int modInverse(unsigned long long int e, unsigned long long int phi) {
        long long int a = e, b = phi;
        long long int originalPhi = phi;
        long long int x = 0, y = 1, lastx = 1, lasty = 0;

        while (b != 0) {
            long long int quotient = a / b;

            long long int temp = b;
            b = a % b;
            a = temp;

            temp = x;
            x = lastx - quotient * x;
            lastx = temp;

            temp = y;
            y = lasty - quotient * y;
            lasty = temp;
        }

        if (lastx < 0) lastx += originalPhi;

        return lastx;
    }

    unsigned long long int modPow(unsigned long long int exponent, unsigned long long int base, unsigned long long int modulus) {
        if (modulus == 1) return 0; // Invalid modulus case

        unsigned long long int result = 1;
        base = base % modulus;

        while (exponent > 0) {
            if (exponent & 1) {
                result = (result * base) % modulus;
            }
            exponent = exponent >> 1;
            base = (base * base) % modulus;
        }

        return result;
    }
};

PYBIND11_MODULE(RSAEncryption, m) {
    py::class_<KeyGeneration>(m, "KeyGeneration")
        .def(py::init<>())
        .def("encrypt", &KeyGeneration::encrypt)
        .def("decrypt", &KeyGeneration::decrypt)
        .def("generateKeys", &KeyGeneration::generateKeys);
}