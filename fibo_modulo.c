#include <stdio.h>

long long a, b;
void fib(long long n, long long m) {
    if (n == 0) { 
        a = 0;
        b = 1 % m;
        return;
    }

    fib(n / 2, m);

    long long c = a * ((2 * b % m - a + m) % m) % m;  // F(2k)
    long long d = (a * a % m + b * b % m) % m;        // F(2k+1)

    if (n % 2 == 0) {      // n chẵn: n = 2k
        a = c;
        b = d;
    } else {               // n lẻ: n = 2k+1
        a = d;
        b = (c + d) % m;
    }
}

int main() {
    long long n, m;
    scanf("%lld %lld", &n, &m);
    fib(n, m);
    printf("%lld\n", a);
    return 0;
}
