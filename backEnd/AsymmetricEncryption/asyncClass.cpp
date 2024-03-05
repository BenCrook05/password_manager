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

    py::tuple generateKeys(bool random = true, string s = ""){
        unsigned long long int p, q, e, d, n, maxD;
        if (random){
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
        } else if (!random) {
            int count = 0;
            do{
                pair<unsigned long long int, unsigned long long int> pq = findpqFromString(s);
                p = pq.first;
                q = pq.second;
                unsigned long long int totient = eulerTotient(p, q);
                e = gete(totient);
                d = modInverse(e, totient);
                n = p * q;
                maxD = n  - 1;

                std::string end = s.substr(s.length() - 3, s.length());
                int num = std::stoi(end);
                num = num + count;
                count++;
                std::string add_on = std::to_string(num);
                s = s + add_on;
                s = s.substr(3, s.length());

            } while (d == -1 || d > maxD, q == -1);
        }
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

    std::pair<unsigned long long int, unsigned long long int> findpqFromString(const string& s) {
        unsigned long long int p = -1, q = -1;

        for (size_t length = 3; length <= s.length(); ++length) {
            for (size_t index = 0; index <= s.length() - length; ++index) {
                try {
                    string substr = s.substr(index, length);
                    unsigned long long int num = std::stoull(substr);
                    if (isPrime(num) && num >= 40 && num <= 800) {
                        if (p == -1) {
                            p = num;
                        } else if (q == -1 && num != p) {
                            q = num;
                            return std::make_pair(p, q);
                        }
                    }
                } catch (const std::invalid_argument& e) {
                    continue;
                } catch (const std::out_of_range& e) {
                    continue;
                }
            }
        }

        return std::make_pair(p, q);
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