# OS Release Performance Differences Report

## Executive Summary
- **CPUs Analyzed**: 3 CPUs with data for multiple OS releases
- **Total Data Points**: 588 test results
- **OS Releases Compared**: r7 vs r9

## Overall Performance Comparison

| OS Release | ACES Version | Count | Mean (ms) | Median (ms) | Std Dev |
|------------|--------------|-------|-----------|-------------|---------|
| r7 | ACES 1.0 | 156.0 | 302.85 | 0.32 | 565.17 |
| r7 | ACES 2.0 | 158.0 | 2561.87 | 2.2 | 4802.11 |
| r9 | ACES 1.0 | 137.0 | 249.79 | 0.32 | 428.76 |
| r9 | ACES 2.0 | 137.0 | 994.57 | 2.06 | 1738.53 |

## Performance Improvements (r7 -> r9)

**ACES 1.0:**
- r7 Mean: 302.85ms
- r9 Mean: 249.79ms
- **Improvement: 17.5%** (faster)

**ACES 2.0:**
- r7 Mean: 2561.87ms
- r9 Mean: 994.57ms
- **Improvement: 61.2%** (faster)

## Individual CPU Analysis

### Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz

| OS Release | ACES Version | Count | Mean (ms) | Median (ms) |
|------------|--------------|-------|-----------|-------------|
| r7 | ACES 1.0 | 48.0 | 278.03 | 0.32 |
| r7 | ACES 2.0 | 50.0 | 2363.04 | 2.51 |
| r9 | ACES 1.0 | 43.0 | 216.27 | 0.28 |
| r9 | ACES 2.0 | 40.0 | 928.61 | 1.42 |

**Performance Changes:**
- ACES 1.0: 22.2% improvement
- ACES 2.0: 60.7% improvement

### Intel(R) Xeon(R) CPU E5-2687W v3 @ 3.10GHz

| OS Release | ACES Version | Count | Mean (ms) | Median (ms) |
|------------|--------------|-------|-----------|-------------|
| r7 | ACES 1.0 | 54.0 | 364.33 | 0.37 |
| r7 | ACES 2.0 | 54.0 | 3008.66 | 2.2 |
| r9 | ACES 1.0 | 48.0 | 298.52 | 0.4 |
| r9 | ACES 2.0 | 48.0 | 1236.38 | 2.11 |

**Performance Changes:**
- ACES 1.0: 18.1% improvement
- ACES 2.0: 58.9% improvement

### Intel(R) Xeon(R) W-2295 CPU @ 3.00GHz

| OS Release | ACES Version | Count | Mean (ms) | Median (ms) |
|------------|--------------|-------|-----------|-------------|
| r7 | ACES 1.0 | 54.0 | 263.42 | 0.27 |
| r7 | ACES 2.0 | 54.0 | 2299.19 | 2.29 |
| r9 | ACES 1.0 | 46.0 | 230.27 | 0.36 |
| r9 | ACES 2.0 | 49.0 | 811.53 | 1.71 |

**Performance Changes:**
- ACES 1.0: 12.6% improvement
- ACES 2.0: 64.7% improvement
