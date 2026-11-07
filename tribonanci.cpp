#include <bits/stdc++.h>
using namespace std;

long long m = 1000000007;
long long f[1000001];

int main() {
	int T;
	cin >> T;
	
	f[1] = 0;
	f[2] = 1;
	f[3] = 1;
	
	for (int i = 4; i <= 1000000; i++) {
	    f[i] = (f[i-1] + f[i-2] + f[i-3]) % m;
	}
	
	for (int j = 1; j <= T; j ++) {
	    int n;
	    cin >> n;
	    
	    cout << f[n] << endl;
	}
	
	return 0;

}
