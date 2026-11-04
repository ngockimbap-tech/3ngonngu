#include <stdio.h>

int count_prime(long long n, int prime) {
    int count = 0;
    while (n > 0) {
        if (n % 10 == prime) {
            count++;
        }
        n /= 10;
    }
    return count;
}

int main() {
	long long n;
	scanf("%lld", &n);
	
	int count2 = count_prime(n, 2);
    int count3 = count_prime(n, 3);
    int count5 = count_prime(n, 5);
    int count7 = count_prime(n, 7);
	
	printf("%d\n%d\n%d\n%d\n", count2, count3, count5, count7);

}

