#include <bits/stdc++.h>
using namespace std;

int main() {
    int N;
    long long S;
    cin >> N >> S;

    long long tong = 0;
    int dem = 1;

    for (int i = 1; i <= N; i++) {
        long long x;
        cin >> x;

        if (tong + x > S) {
            dem++;
            tong = x;
        }
        else {
            tong += x;
        }
    }

    cout << dem;

    return 0;
}
