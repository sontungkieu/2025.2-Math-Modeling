import numpy as np
import csv
import json
import os
from model import simulate

experiment_name = 'exp2'
output_fn = f'output/{experiment_name}.csv'
config_fn = f'output/{experiment_name}_config.json'
fieldnames = ['rho', 'b', 'mean_velocity', 'remote_action']
# Constants
config = {
  "L": 17.3,
  "dt": 0.001,
  "T_relax": 3 * 10**5,
  "T_measure": 3 * 10**5,
  "tau": 0.61,
  "a": 0.36,
  "v0_mean": 1.24,
  "v0_std": 0.05,
  "e": 0.07,
  "f": 2.0,
}
with open(config_fn, 'w') as f:
  json.dump(config, f, indent=4)
  print(f"Config saved to {config_fn}")
# Parameters
rho_values = np.linspace(0, 2.8, 20)[1:]
params = [
  {'remote_action': False, 'b': 0.56},
  {'remote_action': True, 'b': 0.0},
  {'remote_action': True, 'b': 0.56}
]
b_values = [0, 0.56, 1.06]
with open(output_fn, 'w', newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
  writer.writeheader() 
  for rho in rho_values:
    N = int(np.floor(rho * float(config['L'])))   # Number of pedestrians       
    for param in params:
      rho, mean_velocity = simulate(
          N=N, L=config['L'], dt=config['dt'], T_relax=int(config['T_relax']),
          T_measure=int(config['T_measure']), a=config['a'], b=param['b'], tau=config['tau'],
          v0_mean=config['v0_mean'], v0_std=config['v0_std'],
          use_remote=bool(param['remote_action']), e=config['e'], f=config['f'])
      print(f"rho: {rho:.2f}, b: {param['b']:.2f}, mean_velocity: {mean_velocity:.4f}, remote_action: {param['remote_action']}")
      writer.writerow({
          'rho': rho,
          'b': param['b'],
          'mean_velocity': mean_velocity,
          'remote_action': 1 if param['remote_action'] else 0
      })