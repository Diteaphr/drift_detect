## A2 g00 SYN2-REG (primary): 68 scored drifts; ratio = E10bFT / baseT summed |residual| (>1: E10bFT worse)
cat                             n  post 3000  post 1000   pre 2000
A   both hit                   45      0.981      0.986      0.990
B   E10bFT miss, baseT hit      9      0.982      0.996      0.961
C   E10bFT hit, baseT miss      4      1.032      1.014      1.010
D   both miss                  10      1.001      0.992      0.996
all                            68      0.986      0.989      0.988
R1 category B post-window ratio 0.982 (n=9) -> NO COST
R2 B / A = 0.982 / 0.981 = 1.001 -> no attributable cost
B by drift type: grad n=2 0.996, rec n=6 0.969, sud n=1 1.000
D1's stale misses that E10bFT misses: n=11, post-window ratio 0.990 (of which baseT hit: n=7, 0.985)

## E13 SYN2g69-REG (replication): 236 scored drifts; ratio = E10bFT / baseT summed |residual| (>1: E10bFT worse)
cat                             n  post 3000  post 1000   pre 2000
A   both hit                  173      0.986      0.990      0.993
B   E10bFT miss, baseT hit     18      0.975      0.990      0.990
C   E10bFT hit, baseT miss     30      0.995      0.981      0.971
D   both miss                  15      1.002      1.001      0.995
all                           236      0.987      0.990      0.990
R1 category B post-window ratio 0.975 (n=18) -> NO COST
R2 B / A = 0.975 / 0.986 = 0.989 -> no attributable cost
B by drift type: grad n=4 0.966, inc n=4 0.970, rec n=5 0.991, sud n=5 0.977

D4 conclusion: both data sets read NO COST with R2 <= 1.05 -> the regression stale reference is a limit of the recall METRIC, not an open problem of the method
