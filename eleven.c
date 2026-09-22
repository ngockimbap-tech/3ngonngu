#include <stdio.h>
#include <stdlib.h>

int n_odd_max, n_even_max;

int check(int n_odd, int n_even, int *pn_odd, int *pn_even) {
    if (n_odd < 0 || n_even > n_even_max) {
        return -1;
    }
    if (n_odd <= n_odd_max && abs(n_odd - n_even)%11 == 0) {
        *pn_odd = n_odd;
        *pn_even = n_even;
        return 1;
    }
    else {
        return check(n_odd - 1 , n_even + 1, pn_odd, pn_even);
    }
}

int main() {
    int x,y;
    scanf("%d %d", &x, &y);
    int N = x+y;
    n_even_max = N/2;
    n_odd_max = (N+1)/2;
    
    if (N > 22 || x <1) {
        printf("%d", -1);
        return 0;
    }
    
    int n_odd = 0;
    int n_even = 0;
    
    if (check(x,0, &n_odd, &n_even) == -1) {
        printf("%d", -1);
    }
    else {
        int num_list[22];
            
        for (int i=0; i<N; i++) {
            if (i%2==0) {
                if (n_odd!=0) {
                    num_list[i] = 1;
                    n_odd -= 1;
                }
                else {
                    num_list[i] = 0;
                }
            }
            else {
                if (n_even!=0) {
                    num_list[i] = 1;
                    n_even -= 1;
                }
                else {
                    num_list[i] = 0;
                }
            }
        }
        
        for (int i=0; i<N; i++) {
            printf("%d", num_list[i]);
        }
    }
    return 0;
}
