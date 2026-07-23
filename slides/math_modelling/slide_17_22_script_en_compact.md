# Compact Presentation Script for Slides 17-22

This is a shorter English version of `slide_17_22_script_en.md`, reduced by about 30% while keeping the main speaking points and chart explanations.

## Slide 17 - Time Stepping: Corrective Algorithm - Visual Summary

### Speaker script

This slide summarizes how the simulation handles collisions after each Euler step.

In the one-dimensional setting, pedestrians move in the positive `x` direction, so the front pedestrian of pedestrian `i` is pedestrian `i+1`. The distance to the front pedestrian is computed with periodic boundary conditions.

The algorithm has four main steps. First, we **predict** the new velocity and position using one Euler step. Second, we **check** whether the actual gap `s_i` to the front pedestrian is smaller than the required length `d_i = a + b v_i`. If this happens, the predicted state violates the hard-body condition.

Third, we **correct** the violation: pedestrian `i` is stopped, its velocity is set to zero, and its position is restored to the old position. Finally, we **propagate** the correction. Since pedestrian `i` has stopped, pedestrian `i-1` behind it may now be too close, so we recheck the following pedestrian. This repeats until no overlap remains.

The key idea is that a collision correction can create a cascade backward through the line, especially under periodic boundary conditions.

### Figure explanation

- Row 1 shows prediction: pedestrian `i` moves toward pedestrian `i+1`.
- Row 2 checks the actual gap `s_i` against the required length `d_i`.
- Row 3 corrects the violation by restoring the old position and setting velocity to zero.
- Row 4 shows cascade propagation to the following pedestrian `i-1`.
- Under periodic boundaries, the same rule also applies across the end of the corridor: the front pedestrian may wrap around to the beginning.

### Closing sentence

Each time step predicts motion first, then enforces the hard-body constraint consistently across the single-file system.

## Slide 18 - Simulation Setup

### Speaker script

This slide gives the simulation setup used for the experiments.

We simulate a one-dimensional periodic corridor with length `L = 17.3 m`. When a pedestrian reaches the end of the corridor, they re-enter from the beginning, so the density remains fixed.

The desired speed is sampled from an approximately normal distribution with mean `mu = 1.24 m/s` and standard deviation `sigma = 0.05 m/s`. The relaxation time is `tau = 0.61 s`, which controls how quickly pedestrians adjust toward their desired speed. The minimum stationary space is `a = 0.36 m`.

For each configuration, we first run `3 x 10^5` relaxation steps to remove the transient phase. Then we run another `3 x 10^5` measurement steps to compute the mean velocity.

The empirical reference points in later plots are digitized from Seyfried et al. (2005), and they are used to compare the shape of our velocity-density curves.

### Content explanation

- Density is computed as `rho = N / L`.
- `v0_mean` and `v0_std` define the desired walking speed distribution.
- `tau` controls velocity relaxation.
- `a` is the static spacing term in `d_i(t) = a + b v_i(t)`.
- Long relaxation and measurement phases make the results less dependent on initialization.

### Closing sentence

The following experiments use this same baseline and vary only selected parameters such as `b`, remote action, or `a`.

## Slide 19 - Hard-body Model without Remote Action

### Speaker script

This slide studies the hard-body model without remote action and focuses on the parameter `b` in `d_i = a + b v_i`.

The x-axis is density `rho`, and the y-axis is mean velocity. The gray points are empirical data from Seyfried 2005. The colored curves show simulations for `b = 0`, `b = 0.56`, and `b = 1.06`.

When `b = 0`, the required space is only the constant `a`. This means pedestrians use the same minimum spacing regardless of whether they move fast or slowly. The blue curve then keeps velocity too high at medium and high densities, so it does not match the empirical trend.

With `b = 0.56 s`, required space increases with velocity. Faster pedestrians need more space, while slower pedestrians need less. The orange curve follows the empirical points much more closely and gives a more realistic curvature.

With `b = 1.06 s`, the velocity-dependent spacing is too strong. The model predicts congestion too early, so the purple curve drops too quickly.

The conclusion is that the hard-body model needs velocity-dependent spacing, meaning `b > 0`. Among the tested values, `b = 0.56 s` gives the best match.

### Chart explanation

- x-axis: density `rho = N/L`; y-axis: mean velocity after relaxation.
- Gray diamonds are empirical reference points, not simulation output.
- Blue `b = 0` overestimates speed at high density.
- Orange `b = 0.56` best captures the empirical decrease.
- Purple `b = 1.06` makes spacing too restrictive.
- Physically, `b` represents the extra space needed when pedestrians move faster.

### Closing sentence

Without remote action, matching empirical data mainly depends on the velocity-dependent spacing term.

## Slide 20 - Hard-body Model with Remote Action

### Speaker script

This slide adds remote action and checks whether long-range interaction changes the macroscopic velocity-density curve.

The blue curve is the calibrated baseline: no remote action with `b = 0.56`. The orange curve uses remote action with `b = 0`. The purple curve uses remote action with `b = 0.56`.

The first observation is that when `b = 0.56`, adding remote action does not strongly change the overall curve. The purple curve stays close to the baseline trend, so the calibrated hard-body spacing already captures most of the macroscopic behavior.

The second observation is more important. When `b = 0`, remote action creates an unphysical velocity gap around `rho approximately 1.2 1/m`. The orange curve stays fast for a while, then drops sharply. Instead of a smooth transition from free flow to congestion, the system jumps suddenly into a jammed regime.

This means remote action cannot replace the velocity-dependent spacing law. If spacing is fixed, the model can still produce unrealistic macroscopic behavior.

### Chart explanation

- All curves use the same density and mean-velocity axes as slide 19.
- Blue: no remote action, `b = 0.56`, used as the calibrated baseline.
- Purple: remote action, `b = 0.56`, close to the baseline.
- Orange: remote action, `b = 0`, showing the velocity gap.
- The gap indicates a sudden transition rather than a smooth slowdown.
- This is why the slide emphasizes that remote action only becomes problematic when the spacing law ignores velocity.

### Closing sentence

Remote action alone is not enough; a realistic fundamental diagram still requires `d_i` to depend on velocity.

## Slide 21 - Microscopic Mechanism: Stop-and-Go Waves

### Speaker script

This slide explains the microscopic mechanism behind the velocity gap by plotting pedestrian positions over time.

The figure has two panels. The left panel is `rho = 1.16 1/m`, and the right panel is `rho = 1.21 1/m`. These densities are close, but they are near the instability threshold for the `b = 0` case.

The x-axis is position in the periodic corridor, and the y-axis is frame index. Time increases from top to bottom. Gray circles show all pedestrians, while black points track one selected pedestrian.

At `rho = 1.16`, the highlighted trajectory is relatively regular. There are small fluctuations, but no clear stop-and-go wave. At `rho = 1.21`, only slightly higher density, the pattern becomes less stable. We see denser clusters and stronger slow-down phases.

This shows that the velocity gap is not only an artifact of averaging. It comes from a microscopic instability: a leader slows down, followers brake, and the disturbance propagates backward as a stop-and-go wave. If `b > 0`, slower pedestrians also require less space, which adds damping and suppresses these artificial waves.

### Chart explanation

- x-axis: periodic position `x`.
- y-axis: frame index, with time increasing downward.
- Gray circles: all pedestrians at each frame.
- Black points: one tracked pedestrian.
- A smooth diagonal trace means the pedestrian keeps moving at a relatively stable rate.
- Dense or nearly vertical segments indicate local slow-down or stopping.
- Comparing the two panels shows how a small density increase can amplify oscillations.

### Closing sentence

Stop-and-go waves explain why a small increase in density can cause a large drop in mean velocity.

## Slide 22 - Parameter Analysis: New Sweep

### Speaker script

After analyzing `b` and remote action, we introduce a new parameter sweep for the analysis section. Instead of varying velocity dispersion or corridor length again, we vary the baseline required space `a`.

The required length is:

```text
d_i(t) = a + b v_i(t)
```

Here, `b` controls how spacing grows with velocity, while `a` is the baseline space that remains even when pedestrians move slowly or stop.

In this sweep, we keep `b = 0.56 s`, `tau = 0.61 s`, and `L = 17.3 m` fixed. Then we test `a = 0.30 m`, `0.36 m`, and `0.42 m`.

The question is how changing this baseline footprint shifts the onset of congestion. Physically, a larger `a` means each pedestrian needs more space at all speeds, so the effective packing capacity becomes lower and congestion should begin earlier.

### Content explanation and transition

- This slide sets up the parameter sensitivity plot on the next slide.
- `a` affects every pedestrian at every time step because it does not depend on velocity.
- At low density, changing `a` should have little effect because pedestrians have enough space.
- At higher density, larger `a` activates hard-body blocking earlier.
- Transition: "On the next slide, the curves confirm this: they are close at low density but separate clearly as density increases."

### If explaining the next plot

- x-axis: density `rho`.
- y-axis: mean velocity.
- Curves: `a = 0.30`, `a = 0.36`, and `a = 0.42`.
- At low density, these curves should remain close because the hard-body constraint is rarely active.
- Larger `a` leads to an earlier velocity drop.
- This means `a` shifts the congestion onset even when `b` is already fixed at the best-fit value.

### Closing sentence

`b` controls dynamic spacing, while `a` controls baseline footprint; both need calibration for a realistic fundamental diagram.
