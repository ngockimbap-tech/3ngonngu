#include <bits/stdc++.h>
using namespace std;

int main() {
	int n;
	cin >> n;
	
	int a[1000];
	
	for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    
    int b[1000];
    int m = 0;
    
    for (int i = n - 1; i >= 0; i--) {
        bool found = false;
        
        for (int j = 0; j < m; j++) {
            if (a[i] == b[j]) {
                found = true;
                break;
            }
        }
        
        if (found == false) {
            b[m] = a[i];
            m++;
        }
    }
    
    for (int i = 0; i < m; i++) {
        cout << b[i] << " ";
    }
    
	return 0;

}
