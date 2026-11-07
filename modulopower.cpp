#include <bits/stdc++.h>
using namespace std;

long long m = 1000000007;

int A[1000001];

long long modpow(long long x, int y) {
    long long s = 1;

    while (y > 0) {
        if (y % 2 == 1) {
            s = (s * x) % MOD;
        }

        y /= 2;

        if (y > 0) {
            x = (x * x) % MOD;
        }
    }

    return s;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    long long ans = 0;

    for (int i = 0; i < N; i++) {
        int b;
        cin >> b;

        ans = (ans + modpow(A[i], b)) % MOD;
    }

    cout << ans;

    return 0;
}
