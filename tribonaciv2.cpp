#include <bits/stdc++.h>
using namespace std;

long long f[51];

int main() {
    int n;
    cin >> n;

    f[1] = 0;
    f[2] = 0;
    f[3] = 1;

    for (int i = 4; i <= n; i++) {
        f[i] = f[i-1] + f[i-2] + f[i-3];
    }

    for (int i = 1; i <= n; i++) {
        cout << f[i] << " ";
    }

    return 0;
}
