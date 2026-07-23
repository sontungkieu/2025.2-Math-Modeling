# Presentation Script for Slides 17-22

This file is the English presentation script based on `slide_17_22_script.md`.
Each slide has two parts:

- **Speaker script**: the part that can be spoken directly during the presentation.
- **Figure/chart explanation**: extra detail for explaining the visual or answering questions.

Note: in the current PDF, slide 22 introduces the parameter sweep for `a`; the actual plot for this sweep is on slide 23. The slide 22 section below includes a transition sentence to the next plot.

## Slide 17 - Time Stepping: Corrective Algorithm - Visual Summary

### Speaker script

On this slide, I summarize how the simulation handles collisions after each Euler time step.

In the one-dimensional model, all pedestrians have a positive intended direction along the `+x` axis. Therefore, the pedestrian in front of pedestrian `i` is defined as pedestrian `i+1`, and the front distance is computed under the periodic boundary condition of the corridor.

The algorithm has four steps. The first step is **predict**: from the current velocity and force, we compute the new velocity and the new position using one Euler step. The second step is **check**: we compare the actual gap `s_i` from pedestrian `i` to pedestrian `i+1` with the required length `d_i = a + b v_i`. If `s_i` is smaller than `d_i`, the Euler prediction has created an invalid state where pedestrians overlap or become too close.

The third step is **correct**: pedestrian `i` is stopped, its velocity is set to zero, and its position is restored to the old position before the Euler step. The fourth step is **propagate**: when pedestrian `i` is stopped, the following pedestrian `i-1` may now be too close to pedestrian `i`, so we have to check that pedestrian again. This process is repeated until there is no overlap anywhere in the system.

The important point is that collision correction is not an isolated update for one pedestrian. In single-file motion, stopping one pedestrian can trigger a chain reaction backward through the queue. With periodic boundary conditions, this cascade can even wrap around the whole corridor.

### Figure explanation

- The first row illustrates the **Predict** step. The blue point is pedestrian `i`, and the red point is pedestrian `i+1`, which is the pedestrian in front. The dashed arrow shows the predicted new position of pedestrian `i` after one Euler step.
- The second row shows the **Check** step. The segment `s_i` is the actual gap after prediction. The segment `d_i` is the minimum required length in the model. When `s_i <= d_i`, the hard-body condition is violated.
- The third row shows the **Correct** step. Pedestrian `i` is not allowed to keep the predicted position. Instead, it is moved back to the old position, and its velocity is set to zero. This preserves the no-overtaking and no-overlap constraints.
- The last row shows **Propagate / Cascade**. Once pedestrian `i` stops, pedestrian `i-1` behind it may no longer have enough space, so `i-1` must be rechecked. This is the microscopic origin of queue formation in the simulation.
- If asked about periodic boundaries: distances are interpreted modulo `L`, so a pedestrian near the end of the corridor can still have its front pedestrian near the beginning of the corridor.

### Closing sentence

This slide defines the microscopic consistency of the model: each time step first predicts motion, then corrects all hard-body violations in a single-file order.

## Slide 18 - Simulation Setup

### Speaker script

This slide summarizes the simulation setup used in our experiments.

The environment is a one-dimensional corridor with periodic boundary conditions and length `L = 17.3 m`. This means that when a pedestrian reaches the end of the corridor, they re-enter from the beginning, so the pedestrian density stays constant during the simulation.

The desired walking speed is sampled from an approximately normal distribution with mean `mu = 1.24 m/s` and standard deviation `sigma = 0.05 m/s`. The parameter `tau = 0.61 s` is the relaxation time, which controls how quickly a pedestrian adjusts from the current velocity toward the desired velocity. The parameter `a = 0.36 m` is the minimum stationary space.

For the simulation protocol, each configuration is first run for `3 x 10^5` relaxation steps, so the initial transient behavior is removed. Then we run another `3 x 10^5` measurement steps to compute the mean velocity and construct the fundamental diagram.

The empirical points used in the following plots are extracted by plot digitization from the Seyfried et al. (2005) reference. They are used as a comparison target for the shape of the velocity-density relation.

### Content explanation

- `L = 17.3 m` is the length of the periodic corridor; density is computed as `rho = N / L`.
- `v0_mean = 1.24 m/s` is the average desired free walking speed.
- `v0_std = 0.05 m/s` introduces small differences between pedestrians, so the system is not perfectly homogeneous.
- `tau = 0.61 s` controls the strength of relaxation toward the desired speed.
- `a = 0.36 m` is the static part of the required length in `d_i(t) = a + b v_i(t)`.
- Long relaxation and measurement phases reduce the dependence of the results on the initial condition.

### Closing sentence

All the following plots use this same simulation baseline; we only change selected parameters such as `b`, remote action, or `a` to isolate their effects.

## Slide 19 - Hard-body Model without Remote Action

### Speaker script

This slide answers the question: if we use only the hard-body constraint and no remote action, how does the parameter `b` in `d_i = a + b v_i` affect the fundamental diagram?

The horizontal axis is the density `rho`, with unit `1/m`. The vertical axis is the mean velocity, with unit `m/s`. The gray points are the empirical data from Seyfried 2005. The three colored curves are our simulation results for three values of `b`: `b = 0`, `b = 0.56`, and `b = 1.06`.

When `b = 0`, the required space is only the constant value `a`. This means that pedestrians use the same minimum spacing whether they are moving fast or slowly. As a result, the blue curve does not follow the empirical trend: the velocity remains too high at medium and high densities, so the shape of the fundamental diagram is incorrect.

When `b = 0.56 s`, the required space increases with velocity. Faster pedestrians need more space, while slower pedestrians require less space. The orange curve therefore follows the empirical trend more closely: velocity decreases more smoothly with density, and the overall curvature is more realistic.

When `b = 1.06 s`, the velocity-dependent spacing is too strong. Pedestrians require too much space when they move fast, so the model predicts congestion too early, and the velocity drops too rapidly compared with the empirical data.

The conclusion is that the hard-body model can reproduce the empirical data only when the required space depends on velocity, meaning `b > 0`. Among the tested values, `b = 0.56 s` gives the most reasonable match to the Seyfried data.

### Chart explanation

- **x-axis**: density `rho = N/L`. As `rho` increases, there are more pedestrians in the same corridor length.
- **y-axis**: mean velocity measured after the relaxation phase.
- **Gray points**: digitized empirical data. These points are a reference for the correct shape, not simulation output.
- **Blue curve, `b = 0`**: required length does not depend on speed. This curve overestimates velocity at high density and misses the correct congestion onset.
- **Orange curve, `b = 0.56`**: produces a smoother velocity decrease and is closest to the empirical trend among the three curves.
- **Purple curve, `b = 1.06`**: spacing grows too strongly with velocity, so the flow becomes restricted too early.
- **Physical interpretation**: `b` is not just a fitting parameter. It represents the fact that pedestrians need more space when they move faster.

### Closing sentence

Without remote action, the key component needed to match the empirical trend is the velocity-dependent required space: `d_i = a + b v_i`.

## Slide 20 - Hard-body Model with Remote Action

### Speaker script

This slide adds remote action to the model and examines whether long-range interaction changes the fundamental diagram.

The three curves use the same axes as the previous slide: density on the horizontal axis and mean velocity on the vertical axis. The blue curve is the baseline case without remote action and with `b = 0.56`. The orange curve uses remote action but `b = 0`. The purple curve uses both remote action and `b = 0.56`.

The first result is that when `b = 0.56`, adding remote action does not significantly change the overall shape of the curve. Some high-density points may become lower, but the main behavior is still a continuous decrease from free flow to congested flow. This suggests that once the required space is calibrated with velocity, the hard-body constraint already captures most of the macroscopic behavior.

The second and more important result is that when `b = 0`, remote action creates an unphysical "velocity gap" around `rho` approximately equal to `1.2 1/m`. The orange curve keeps a high velocity over a range of densities, then drops sharply. This means the transition from free flow to congestion is no longer smooth.

The explanation is that remote action adds a long-range braking or repulsive force, but it cannot replace a correct velocity-dependent spacing law. If `b = 0`, pedestrians are still forced to use a fixed required length, so once density crosses a threshold, the system can suddenly collapse into a jammed state.

### Chart explanation

- **Blue curve**: no remote action, `b = 0.56`. This is the calibrated baseline from the previous slide.
- **Purple curve**: remote action, `b = 0.56`. Its trend is close to the baseline, which means remote action is not the dominant factor when `b` is already reasonable.
- **Orange curve**: remote action, `b = 0`. Velocity remains high at low-to-medium densities but then drops sharply. This is the velocity gap.
- **Velocity gap**: instead of decreasing gradually with density, the system jumps from a fast-moving state to a congested state.
- **Model message**: remote action can represent anticipatory braking, but if the spacing law is wrong, the macroscopic result is still wrong.

### Closing sentence

Remote action does not fix the problem of `b = 0`. A realistic fundamental diagram still requires the required space to depend on velocity.

## Slide 21 - Microscopic Mechanism: Stop-and-Go Waves

### Speaker script

This slide looks at the microscopic mechanism behind the velocity gap. Instead of only showing the mean velocity, we now plot the positions of all pedestrians over time.

The figure has two panels. The left panel corresponds to `rho = 1.16 1/m`, and the right panel corresponds to `rho = 1.21 1/m`. These two densities are very close, but they are near the threshold where the `b = 0` model starts to become unstable. The horizontal axis is position `x` on the periodic corridor of length `17.3 m`. The vertical axis is the frame index, and time increases from top to bottom. The gray circles show the positions of all pedestrians at each frame, while the black points track one selected pedestrian.

At the lower density, the highlighted trajectory is relatively regular. The system still has interactions and small fluctuations, but it does not show a clear stop-and-go wave. When the density increases only slightly to `rho = 1.21`, denser clusters appear and the highlighted pedestrian shows more visible slow-down or stopping phases. This is the signature of a stop-and-go wave: a leading pedestrian slows down, the followers brake sharply, and the disturbance travels backward through the line.

The key point is that the velocity gap in slide 20 is not just an artifact of an averaged plot. It has a microscopic mechanism: after a density threshold, small spacing fluctuations are amplified into stop-and-go waves. If `b > 0`, then when a pedestrian slows down, the required space `d(v)` also decreases. This creates natural damping and makes such artificial waves harder to amplify.

### Chart explanation

- **x-axis**: position `x` in the periodic corridor. When a pedestrian passes the end of the corridor, the position wraps back near zero.
- **y-axis**: frame index. Because the y-axis is inverted, time increases from top to bottom.
- **Gray circles**: all pedestrians at each frame. Each horizontal band is close to one system snapshot.
- **Black points**: one tracked pedestrian, used to visualize the motion of an individual rather than only the whole crowd.
- **Smooth diagonal point sequence**: relatively stable walking motion.
- **Dense clusters or nearly vertical segments**: slow-down or stopping behavior over multiple frames, which indicates local congestion.
- **Comparison between panels**: increasing density from `1.16` to `1.21 1/m` is small, but the system changes from almost stable motion to amplified oscillations.
- **Connection to slide 20**: this explains why the velocity-density curve can drop suddenly when `b = 0`.

### Closing sentence

Stop-and-go waves are the microscopic mechanism that explains why a small increase in density can cause a large decrease in mean velocity.

## Slide 22 - Parameter Analysis: New Sweep

### Speaker script

After analyzing `b` and remote action, this slide introduces a new parameter sweep for the analysis section, so that our analysis is not only repeating velocity dispersion or corridor-length variation.

The varied parameter is `a` in the formula:

```text
d_i(t) = a + b v_i(t)
```

If `b` is the additional spacing that grows with velocity, then `a` is the baseline spacing. It is the minimum required space that remains active even when a pedestrian is moving very slowly or almost stopped.

In this sweep, we keep the main parameters fixed: `b = 0.56 s`, `tau = 0.61 s`, and `L = 17.3 m`. Then we test three values of `a`: `0.30 m`, `0.36 m`, and `0.42 m`.

The question is: if we only change the baseline size of each pedestrian, how does the congestion onset shift? The physical expectation is that a larger `a` means pedestrians need more space at every speed. Therefore, the effective packing capacity becomes lower, and congestion should appear earlier.

### Content explanation and transition to the next plot

- This slide is not the plot yet. It sets up the parameter sensitivity plot on the next slide.
- `a` affects every pedestrian at every time step because it does not depend on velocity.
- At low density, pedestrians rarely hit the hard-body constraint, so changing `a` should not strongly separate the curves.
- At medium and high density, the hard-body constraint becomes active more often. In this regime, a larger `a` should reduce velocity earlier.
- Transition sentence: "On the next slide, we can see exactly this trend in the fundamental diagram: the curves are close at low density, but they separate clearly as density increases."

### If explaining the `a` sweep plot on the next slide

- **x-axis**: density `rho`.
- **y-axis**: mean velocity.
- **Three curves**: `a = 0.30`, `a = 0.36`, and `a = 0.42`.
- **Low-density region**: the curves remain close because pedestrians still have enough space.
- **High-density region**: `a = 0.42` drops fastest, while `a = 0.30` maintains higher velocity.
- **Conclusion**: calibrating `a` shifts the congestion onset even when `b` is fixed at the best-fit value.

### Closing sentence

`b` controls the dynamic spacing that depends on velocity, while `a` controls the baseline footprint. To obtain a realistic fundamental diagram, the model needs calibration of both components.
