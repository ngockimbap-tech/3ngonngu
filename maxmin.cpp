#include <bits/stdc++.h>
using namespace std;

long long A[1001], B[1001];

int main() {
    int N;
    cin >> N;

    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    for (int i = 0; i < N; i++) {
        cin >> B[i];
    }

    long long ans = -1000000000000;

    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {

            long long x = A[i] * A[j];
            long long y = B[i] * B[j];

            long long temp = min(x, y);

            ans = max(ans, temp);
        }
    }

    cout << ans;

    return 0;
}
