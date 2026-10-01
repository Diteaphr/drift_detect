# A3 post-hoc diagnosis (descriptive, NOT registered; changes no verdict)

The registered conclusion in `a3_verdict.md` is "boundary condition -- Q1 fails on REALreg-metro".
This note records what the failure consists of. Computed from the stored traces after the verdict.

## The metro MAE is dominated by a handful of exploding predictions of the forest learner (hfr)

Target range on metro_interstate_traffic: 0 .. 7280 (mean 3260).

| learner | arm     | mean \|residual\| | median | p99  | max      | steps > 1e4 | mean without them |
|---------|---------|-------------------|--------|------|----------|-------------|-------------------|
| hfr     | baseT   | 4.94e6            | 1456.2 | 3738 | 1.3e11   | 6           | 1537.3            |
| hfr     | E2k500T | 3.29e6            | 1459.8 | 3737 | 3.9e10   | 10          | 1539.3            |
| hfr     | E10bFT  | 1.88e9            | 1490.1 | 3749 | 9.0e13   | 54          | 1559.1            |
| htr     | baseT   | 1687.3            | 1641.7 | 3892 | 5376     | 0           | 1687.3            |
| htr     | E2k500T | 1677.8            | 1636.4 | 3906 | 5153     | 0           | 1677.8            |
| htr     | E10bFT  | 1675.6            | 1646.5 | 3893 | 5187     | 0           | 1675.6            |

- Every arm has the blow-up on hfr (48,004 steps each); the single tree (htr) never does. bike_sharing has none.
- Several blow-up steps are shared across arms (t = 7414, 8742, 17365, 30080, 45547, 47330-47331), i.e. they are
  driven by particular input rows. The data contain known bad records: one row with rain x2 = 9831.3 (row 24872,
  where E10bFT blows up) and 10 rows with temperature x1 = 0 K.
- E10bFT has 54 blow-up steps against 6 for baseT. It also confirms 17 times on this run against 6; 47 of its 54
  blow-up steps fall within 3,200 steps of its latest confirmation (baseT: 2 of 6). Reading: each confirmation
  installs a young model, and young forest models are the ones that explode on these rows.

## Robust view of Q1 (for description only)

| data set / learner | E10bFT / baseT, mean | without steps > 1e4 | median |
|--------------------|----------------------|---------------------|--------|
| bike hfr           | 1.020                | 1.020               | 0.970  |
| bike htr           | 0.996                | 0.996               | -      |
| metro hfr          | 380.5                | 1.014               | 1.023  |
| metro htr          | 0.993                | 0.993               | 1.003  |

Without the exploding steps the metro data-set ratio (mean of the two learners) is 1617.4 / 1612.3 = 1.003.

## Q2 did not hold either

E10bFT confirms slightly MORE often than baseT on both real streams (bike 12 vs 10, metro 35 vs 29), unlike every
synthetic and injected round, where its false alarms were a fraction of baseT's. baseT itself confirms rarely here
(5 per 17k steps on bike). Only 26% of baseT's and 34% of E10bFT's confirmations follow a real rise in raw residual.
