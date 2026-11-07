#include <bits/stdc++.h>
using namespace std;

long long m = 1000000007;
long long A[1000001];
long long B[1000001];

long long modpow(long long x, long long y) {
    long long s = 1;
    
    while (y > 0) {
        if (y % 2 == 1) {
            s = (s * x) % m;
        }
        
        x = (x * x) % m;
        y /= 2;
    }
    
    return s;
}

int main() {
	int N;
	cin >> N;
	
	for (int i = 0; i < N; i++) {
        cin >> A[i];
    }
    
    long long ans = 0;
    
    for (int i = 0; i < N; i++) {
        cin >> B[i];
        
        ans = (ans + modpow(A[i], B[i])) % m;
    }
	
	cout << ans;
	
	return 0;

}
