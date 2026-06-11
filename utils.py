import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def velocity_density_diagram(csv_path: str):
    # Read the CSV
    df = pd.read_csv(csv_path)

    # Exclude "empirical" if it's encoded in column 'b' (as string or NaN)
    df = df[pd.notna(pd.to_numeric(df['b'], errors='coerce'))]

    # Unique b values to group and plot
    b_unique_values = pd.Series(df['b']).unique()
    for b_value, marker in zip(sorted(b_unique_values), ['o', 's', '^']):
        subset = df[df['b'] == b_value]
        plt.plot(subset['rho'], subset['mean_velocity'], marker=marker, linestyle='None', label=f"b={b_value:.2f}")

    # Labels and legend
    plt.xlabel(r"$\rho$ [1/m]")
    plt.ylabel(r"$v$ [m/s]")
    plt.title("Velocity-Density Diagram (hard bodies, no remote action)")
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 3)
    plt.ylim(0, 1.4)

    output_path = csv_path.replace('.csv', '.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")

def remote_action_comparison(csv_path: str):
    # Read the CSV
    df = pd.read_csv(csv_path)

    # Exclude "empirical" if it's encoded in column 'b' (as string or NaN)
    df = df[pd.notna(pd.to_numeric(df['b'], errors='coerce'))]
    df['remote_action'] = df['remote_action'].astype(int)

    # Define style for each (remote_action, b) pair
    styles = {
        (0, 0.56): {'marker': 'o', 'facecolor': 'green', 'edgecolor': 'black', 'label': 'without remote action, b=0.56'},
        (1, 0.00): {'marker': 's', 'facecolor': 'orange', 'edgecolor': 'black', 'label': 'with remote action, b=0'},
        (1, 0.56): {'marker': 'o', 'facecolor': 'blue', 'edgecolor': 'black', 'label': 'with remote action, b=0.56'}
    }

    for (remote, b_val), style in styles.items():
        subset = df[(df['remote_action'] == remote) & (df['b'] == b_val)]
        if isinstance(subset, pd.DataFrame) and not subset.empty:
            plt.scatter(
                subset['rho'], subset['mean_velocity'],
                marker=style['marker'],
                facecolors=style['facecolor'],
                edgecolors=style['edgecolor'],
                label=style['label'],
                linewidths=1
            )
    # Labels and legend
    plt.xlabel(r"$\rho$ [1/m]")
    plt.ylabel(r"$v$ [m/s]")
    plt.title("Velocity–Density Diagram for hard bodies with and without a remote action")
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 3)
    plt.ylim(0, 1.4)

    output_path = csv_path.replace('.csv', '.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")


def time_development_plot(csv_path: str, output_path= None):
    """
    Plot spatio-temporal evolution of pedestrian positions.

    Parameters:
    - csv_path: str, path to CSV file (no header, each row = time step, each column = pedestrian)
    - output_path: str, where to save the image. If None, saves to csv_path.replace('.csv', '.png')
    """
    # Load the CSV data
    data = np.loadtxt(csv_path, delimiter=',')
    num_steps, num_pedestrians = data.shape

    # Create figure
    plt.figure(figsize=(5, 5))

    # Plot all circles as hollow by default
    for t in range(num_steps):
    #     y = num_steps - t  # flip time for top-down plot
        for i in range(num_pedestrians):
            if i == 1:
                # 4th pedestrian at t=0 → solid black
                plt.plot(data[t, i], t, 'o', markersize=4, markerfacecolor='black', markeredgecolor='black')
            else:
                plt.plot(data[t, i], t, 'o', markersize=4,
                         markerfacecolor='none', markeredgecolor='black')

    # Axis labels and ticks
    plt.xlabel("L")
    plt.ylabel("t")
    plt.xlim(0, 17.3)
    plt.ylim(0, num_steps)
    plt.xticks(range(0, 17, 2))  # even ticks from 0 to 16
    plt.yticks([])               # no y-axis labels
    plt.gca().invert_yaxis()    # time flows top → bottom

    # Title with density estimate
    rho_est = num_pedestrians / 17.3  # assuming L=17.3
    plt.title(f"$\\rho$ ≈ {rho_est:.2f} [1/m]")

    # Save
    if output_path is None:
        output_path = csv_path.replace(".csv", ".png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    output_fn = 'output/exp4.csv'
    time_development_plot(output_fn)
