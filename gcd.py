import math
n, m = map(int, input().split())
a_n = list(map(int, input().split()))
b_m = list(map(int, input().split()))
g=0
for num in a_n[1:]:
    new_num = abs(num - a_n[0])
    g = math.gcd(g,new_num)
for b_i in b_m:
    print(math.gcd(abs(a_n[0] + b_i), g))
