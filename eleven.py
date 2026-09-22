x, y = map(int, input().split())

N = x+y
n_even_max = N // 2
n_odd_max = (N + 1) // 2

def check(n_odd, n_even):
    if n_odd < 0 or n_even > n_even_max:
        return -1
    if n_odd <= n_odd_max and abs(n_odd - n_even)%11 == 0:
        return n_odd, n_even
    return check(n_odd - 1, n_even + 1)
    
if N > 22 or x < 1:
    print(-1)
else:
    if check(x,0) == -1:
        print(-1)
    else:
        n_odd, n_even = check(x,0)
        num_list = []
    
        for i in range (N):
            if i%2 == 0:
                if n_odd != 0:
                    num_list.append(1)
                    n_odd -= 1
                else:
                    num_list.append(0)
            else:
                if n_even != 0:
                    num_list.append(1)
                    n_even -= 1
                else:
                    num_list.append(0)
        print(int("".join(map(str, num_list))))
