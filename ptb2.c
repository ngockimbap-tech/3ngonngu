#include <stdio.h>
#include <math.h>

int main() {
	float a, b, c;
    scanf("%f %f %f",&a, &b, &c);
    if (a!=0) {
        float d = b*b - 4*a*c;
        if (d!=0) {
            if (d>0) {
                float x1 = (-b+sqrt(d))/(2*a);
                float x2 = (-b-sqrt(d))/(2*a);
                printf("Phương trình có 2 nghiệm x1 = %f và x2 = %f", x1, x2);
            }
            else {
                printf("Phương trình vô nghiệm");
            }
        }
        else {
            float x = -b/(2*a);
            printf("Phương trình có nghiệm kép x = %f", x);
            }
        }
    else {
        if (b!=0) {
            float x = -c/b;
            printf("Phương trình có 1 nghiệm x = %f", x);
        }
        else {
            if (c!=0) {
                printf("Phương trình vô nghiệm");
            }
            else {
                printf("Phương trình có vô số nghiệm");
            }
        }
    }
    return 0;
    
}
