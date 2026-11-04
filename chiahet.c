#include <stdio.h>

long long divisible (long long n, long long m) {
	    return n / m;
	}

long long gcd(long long a, long long b) {
    if (b==0) {
        return a;
    }
    else {
        return(gcd(b, a%b));
    }
}

long long lcm(long long a, long long b) {
    if ((a == 0) || (b == 0)) {
        return 0;
    }
    else {
        return a / gcd(a, b) * b;
    }
}

int main() {
	long long n, a, b;
	scanf("%lld %lld %lld", &n, &a, &b);
	
	long long result = divisible(n, a) + divisible(n, b) - divisible(n, lcm(a,b));
	
	printf("%lld", result);

}

