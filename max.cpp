#include <bits/stdc++.h>
using namespace std;

int main() {
	int N, n1, n2, n3, n4, max;
	cin >> N;
	n4 = N%10;
	n3 = (N/10)%10;
	n2 = (N/100)%10;
	n1 = N/1000;
	
	max = n1;
	
	if (n2 > max) {
	    max = n2;
	}
	if (n3 > max) {
	    max = n3;
	}
	if (n4 > max) {
	    max = n4;
	}
	
	cout << max << endl;
	return 0;
}
