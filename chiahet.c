long long gcd(long long x, long long y) {
    if (y==0) {
        return x;
    }
    else {
        return(gcd(y, x%y));
    }
}

long long lcm(long long x, long long y) {
    if ((x == 0) || (y == 0)) {
        return 0;
    }
    else {
        return x / gcd(x, y) * y;
    }
}
