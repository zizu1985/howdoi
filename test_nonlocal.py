from itertools import zip_longest
import copy

if __name__ == '__main__':
    a = [1, 2, 3, 4]
    b = [1, 2]

    for i,j in zip_longest(a,b):
        print(i, j)

    print("Copy example")
    print(a)
    c = copy.copy(a)
    print(c)
    a[0] = 100
    print(a)
    print(c)