## Rescore (classify() with scoring window = GT start + ext)
validity: runs where ext=1000 differs from stored labels = 0
                tp@1000  tp@3000  fp@1000  fp@3000
family  arm                                       
B       E1            4        7        3        0
        E2k0          5        7        8        6
        E2k500        5        6        7        6
        E6            4        8        7        3
        base          6        9       11        6
MC-RBF  E1           14       13        0        0
        E2k0         22       23        1        0
        E2k500       21       20        3        1
        E6           21       20        3        1
        base         22       20       24       18
MC-syn  E1           37       37        5        4
        E2k0         38       38        4        2
        E2k500       37       38        5        1
        E6           37       37        2        0
        base         35       39       48       21
REG-Joe E1           20       23       24       19
        E2k0         20       31       16        5
        E2k500       21       29       13        5
        E6           19       29       13        3
        base         23       29       29       21
REG-syn E1           19       19       10        4
        E2k0         19       20        1        0
        E2k500       20       20        0        0
        E6           20       20        0        0
        base         18       19       20        9

all families:
        tp@1000  tp@3000  fp@1000  fp@3000
arm                                       
E1           94       99       42       27
E2k0        104      119       30       13
E2k500      104      113       28       13
E6          101      114       25        7
base        104      116      132       75
