#include <stdio.h>

int divisible(int n, int m);

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
	int n, a, b;
	scanf("%d %d %d", &n, &a, &b);
	
	int divisible (int n, int m) {
	    return n / m;
	}
	
	int result = divisible(n, a) + divisible(n, b) - divisible(n, lcm(a,b));
	
	printf("%d", result);

}

