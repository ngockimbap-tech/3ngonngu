#include <stdio.h>

long long nCr (int n, int k) {
    if ((k < 0) || (k > n)) {
        return 0;
    }
    if ((k == 0) || (k == n)) {
        return 1;
    }
    
    if (k > n - k) {
        k = n - k;
    }
    
    long long kq = 1;
    for (int i = 1; i <= k; i++) {
        kq = kq * (n - k + i) / i;
    }
    return kq;
}

int main() {
    int k, n;
    scanf("%d %d", &k, &n);
    
    printf("%lld", nCr(n,k));
    
    return 0;
}
