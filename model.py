from collections import deque
import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm
import csv
from utils import time_development_plot

def front_index(i: int, N: int) -> int:
    return (i + 1) % N

def follower_index(i: int, N: int) -> int:
    return (i + N - 1) % N

def distance_to_front(i: int, x: NDArray[np.float64], L: float, N: int) -> float:
    return (x[front_index(i, N)] - x[i]) % L

def get_distance(i: int, x: NDArray[np.float64], L: float, N: int) -> float:
    return distance_to_front(i, x, L, N)

def required_length(v_i: float, a: float, b: float) -> float:
    return a + b * v_i

def compute_force(i: int, x, v, v0, a, b, tau, L, dt, N, use_remote=False, e=0.0, f=0.0) -> float:
    d = required_length(v[i], a, b)
    s = distance_to_front(i, x, L, N)

    if not use_remote:
        if s > d:
            return (v0[i] - v[i]) / tau
        else:
            return -v[i] / dt 
    else:
        repulsion = e / (s - d)**f if (s - d) > 1e-4 else 1e6
        G = float((v0[i] - v[i]) / tau - repulsion)
        return G if v[i] > 0 else max(0, G)

def enforce_no_overlap(
    x_old: NDArray[np.float64],
    x_new: NDArray[np.float64],
    v_new: NDArray[np.float64],
    a: float,
    b: float,
    L: float,
    N: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    pending = deque(range(N - 1, -1, -1))

    while pending:
        i = pending.popleft()
        if distance_to_front(i, x_new, L, N) >= required_length(v_new[i], a, b):
            continue
        if v_new[i] == 0 and x_new[i] == x_old[i]:
            continue

        v_new[i] = 0
        x_new[i] = x_old[i]
        pending.append(follower_index(i, N))

    return x_new, v_new

def simulate(N: int, L: float, dt: float, T_relax: int, T_measure: int,
             a: float, b: float, tau: float, v0_mean: float, v0_std: float,
             use_remote=False, e=0.07, f=2.0, output_file=None, seed: int | None = None):
    rng = np.random.default_rng(seed)
    v0 = rng.normal(loc=v0_mean, scale=v0_std, size=N)
    v = np.zeros(N)
    assert a * N < L, "Too many pedestrians for the given length L."
    x = np.arange(N) * a
    count = 0
    velocities = []

    for t in tqdm(range(T_relax + T_measure)):
        forces = np.array([
            compute_force(i, x, v, v0, a, b, tau, L, dt, N, use_remote, e, f)
            for i in range(N)
        ])

        v_new = np.clip(v + dt * forces, 0, v0)
        x_new = (x + v_new * dt) % L

        x_new, v_new = enforce_no_overlap(x, x_new, v_new, a, b, L, N)

        v = v_new
        x = x_new

        if output_file and t >= T_relax:
            frame_interval = 200  # Save one frame every 200 steps
            if (t - T_relax) % frame_interval == 0 and count < 30:
                with open(output_file, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(x.tolist())
                count += 1


        if t >= T_relax:
            velocities.append(np.mean(v))

    rho = N / L
    mean_velocity = np.mean(velocities)
    return rho, mean_velocity

# === Parameters and run ===
if __name__ == "__main__":
    # Constants
    rho = 1.25
    L = 17.3                # Length of the corridor
    N = int(np.floor(rho * L))                        # Number of pedestrians       
    dt = 0.001              # Time step
    T_relax = 3 * 10**5            # Relaxation time
    T_measure = 3 * 10**5          # Measurement time
    tau = 0.61              # Relaxation time constant
    a, b = 0.36, 0.56              # Parameters for required length
    v0_mean, v0_std = 1.24, 0.05   # Mean and std of initial velocities
    use_remote = True  # Use remote force calculation
    e, f = 0.07, 2.0               # Parameters for remote force calculation
    output_file = 'output/exp5.csv'  # Output file path
    rho, mean_velocity = simulate(
        N=N, L=L, dt=dt, T_relax=T_relax, T_measure=T_measure,
        a=a, b=b, tau=tau, v0_mean=v0_mean, v0_std=v0_std,
        use_remote=use_remote, e=e, f=f, output_file=output_file
    )
    print(f"rho: {rho:.2f}, b: {b:.2f}, mean_velocity: {mean_velocity:.4f}")
    time_development_plot(output_file)
