stick = list(map(int, input().split()))
x,y,z = input().split()
min_w = float('inf') #Dương vô cùng
for i in range (4):
    for j in range (4):
        for k in range (4):
            for m in range (4):
                if (i!=j) and (i!=k) and (i!=m) and (j!=k) and (j!=m) and (k!=m):
                    stick_1 = stick[i]
                    stick_2 = stick[j]
                    stick_3 = stick[k]
                    stick_4 = stick[m]
                    
                    """ Kết hợp nối tiếp
                    Ex: a,b,c,d (k theo thứ tự input) vs + * +
                    B1: (a+b)
                    B2: (a+b)*c
                    B3: (a+b)*c + d """
                    
                    if x == '+':
                        w = stick_1 + stick_2
                    else:
                        w = stick_1 * stick_2
                    if y == '+':
                        w += stick_3
                    else:
                        w *= stick_3
                    if z == '+':
                        w += stick_4
                    else:
                        w *= stick_4
                        
                    """ Kết hợp song song
                    Ex: a,b,c,d (k theo thứ tự input) vs + * +
                    B1: (a+b)
                    B2: (c*d)
                    B3: (a+b)+(c*d) """
                    
                    if x == '+':
                        w1 = stick_1 + stick_2
                    else:
                        w1 = stick_1 * stick_2
                    if y == '+':
                        w2 = stick_3 + stick_4
                    else:
                        w2 = stick_3 * stick_4
                    if z == '+':
                        w_ = w1 + w2
                    else:
                        w_= w1 * w2
                        
                    min_w = min(min_w, w, w_)
print(min_w)
