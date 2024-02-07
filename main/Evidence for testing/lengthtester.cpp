int main() {
    for (int i = 4; i <= 7; ++i) { // For each number length from 4 to 7 digits
        unsigned long long int p, q, e, d, n;
        unsigned long long int maxD = n - 1; // Set the maximum allowed value for d based on the modulus

        do {
            pair<unsigned long long int, unsigned long long int> pq = getpq();
            p = pq.first;
            q = pq.second;
            unsigned long long int totient = eulerTotient(p, q);
            e = gete(totient);
            d = modInverse(e, totient);
            n = p * q;
        } while (d == -1 || d > maxD);

        // For each number length, perform 100 iterations
        for (int j = 1; j <= 100; ++j) {
            unsigned long long int input = rand() % static_cast<unsigned long long int>(pow(10, i));
            unsigned long long int encrypted = encryptKey(input, e, n);
            unsigned long long int decrypted = decryptKey(encrypted, d, n);

            unsigned long long int match = decrypted == input;
            cout << "Input: " << input << " - Match: " << match << endl;
        }
    }

    return 0;
}