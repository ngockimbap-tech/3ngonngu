#include <stdio.h>
#include <stdlib.h>

long long gcd(long long x, long long y) {
    if (y==0) {
        return x;
        
    }
    else {
        return(gcd(y, x%y));
    }
}
    
int main() {
    int n, m;
    scanf("%d %d", &n, &m);
    long long a[n], b[m];
    for (int i=0; i<n; i++) {
        scanf("%lld", &a[i]);
    }
    for (int i=0; i<m; i++) {
        scanf("%lld", &b[i]);
    }
    long long g = 0;
    for (int i=1; i<n; i++) {
        g = gcd(g,llabs(a[i]-a[0]));
    }
    for (int i=0; i<m; i++) {
        printf("%lld\n", gcd(g,a[0]+b[i]));
    }
    return 0;
}