# Performance Labeling Fix

## Issue Description

The fastest/slowest performance labeling in the OCIO version comparison reports was incorrect. The analysis was incorrectly identifying slower performance (higher times) as "fastest" and faster performance (lower times) as "slowest".

## Root Cause

The issue was in the `create_detailed_ocio_comparison_report` method in `src/ocio_performance_analysis/analyzer.py` around line 1708.

The data was being sorted by `"ocio_version"` (alphabetically: 2.4.0, 2.4.1, 2.4.2) instead of by `"mean_avg_time"` (performance-wise: fastest to slowest). This meant:

- `aces_data.iloc[0]` was getting the first version alphabetically (not the fastest performance)
- `aces_data.iloc[-1]` was getting the last version alphabetically (not the slowest performance)

### Example of the Bug

Before the fix, for ACES 2.0:

``` text
Fastest: 2.4.1 (2172.6 ms)  ← WRONG! This is slower
Slowest: 2.4.2 (1837.4 ms)  ← WRONG! This is faster
Performance difference: -15.4%
```

## Solution

Added a separate performance-based sort when determining fastest/slowest comparisons:

**Before:**

``` python
aces_data = self.all_ocio_comparison_data[
    self.all_ocio_comparison_data["aces_version"] == aces_version
].sort_values("ocio_version")  # ← Sorted alphabetically

fastest_aces = aces_data.iloc[0]  # ← First alphabetically
slowest_aces = aces_data.iloc[-1]  # ← Last alphabetically
```

**After:**

``` python
aces_data = self.all_ocio_comparison_data[
    self.all_ocio_comparison_data["aces_version"] == aces_version
].sort_values("ocio_version")  # ← Still sorted alphabetically for display

# Sort by performance for fastest/slowest comparison
aces_data_by_perf = aces_data.sort_values("mean_avg_time")
fastest_aces = aces_data_by_perf.iloc[0]  # ← Fastest performance (lowest time)
slowest_aces = aces_data_by_perf.iloc[-1]  # ← Slowest performance (highest time)
```

## Verification

After the fix, for ACES 2.0:

``` text
Fastest: 2.4.2 (1837.4 ms)  ✓ CORRECT! This is faster (lower time)
Slowest: 2.4.1 (2172.6 ms)  ✓ CORRECT! This is slower (higher time)
Performance difference: 18.2%
```

For ACES 1.0:

``` text
Fastest: 2.4.2 (275.5 ms)   ✓ CORRECT! This is faster (lower time)
Slowest: 2.4.0 (324.2 ms)   ✓ CORRECT! This is slower (higher time)
Performance difference: 17.7%
```

## Files Modified

- `src/ocio_performance_analysis/analyzer.py` - Fixed fastest/slowest comparison logic

## Testing

- All unit tests continue to pass
- CLI commands work correctly  
- Generated reports now show correct fastest/slowest labeling
- Performance difference calculations are accurate

## Impact

This fix ensures that:

1. Performance reports correctly identify the fastest and slowest OCIO versions
2. Users can trust the analysis results for making performance-based decisions
3. Charts and visualizations correctly reflect actual performance differences
