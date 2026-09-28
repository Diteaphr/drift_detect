## V1: E1 detector vs MOA ADWINChangeDetector (CapyMOA), tolerance +-32 steps

drift arm:
         e1_fires  moa_fires  e1_matched  e1_exact  moa_matched  e1->moa  moa->e1  exact
family                                                                                  
B               8         28           1         0            1    0.125    0.036  0.000
MC-RBF         19         38           5         4            6    0.263    0.158  0.211
MC-syn         46        114          38        28           60    0.826    0.526  0.609
REG-Joe        44        111           9         5           11    0.205    0.099  0.114
REG-syn        29         62          20        15           31    0.690    0.500  0.517
pooled: e1->moa 0.500  moa->e1 0.309  exact 0.356
MOA-only fires by source: first 30 steps of a window 0 | re-fire within 32 steps 74 | other 170
V1 verdict (drift arm, both >= 0.90): NOT faithful: describe E1 as 'river ADWIN core + MOA direction semantics'

warning arm:
         e1_fires  moa_fires  e1_matched  e1_exact  moa_matched  e1->moa  moa->e1  exact
family                                                                                  
B               7         31           1         1            2    0.143    0.065  0.143
MC-RBF         15         42           6         2            7    0.400    0.167  0.133
MC-syn         44        104          34        21           49    0.773    0.471  0.477
REG-Joe        47        100          14         7           17    0.298    0.170  0.149
REG-syn        29         53          20        13           30    0.690    0.566  0.448
pooled: e1->moa 0.528  moa->e1 0.318  exact 0.310
MOA-only fires by source: first 30 steps of a window 0 | re-fire within 32 steps 62 | other 163
