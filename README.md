# Local Package Delivery Optimization (AI)

Optimization strategies for local package delivery using **Simulated Annealing** and **Genetic Algorithms**. The project assigns packages to vehicles (respecting capacity) and minimizes a cost function that combines delivery distance and priority-based penalties.

## Features

- **Simulated Annealing** — Assigns packages to vehicles and iteratively improves the solution (neighbor = move one package between vehicles).
- **Genetic Algorithm** — Population-based search: individuals encode package→vehicle assignment; fitness considers priority reward, distance, and capacity penalties.
- **Visualization** — Plots delivery routes from depot (0,0) with package locations and per-vehicle paths.

## Data Files

| File          | Description |
|---------------|-------------|
| `packages.csv` | Columns: `id`, `x`, `y`, `weight`, `priority` (1 = highest) |
| `cars.csv`     | Columns: `id`, `capacity` (max weight per vehicle) |

Packages with `weight > 100` are filtered out when loading for Simulated Annealing. The depot is at (0, 0).

## Requirements

- Python 3.x  
- **matplotlib** (for route plots)

```bash
pip install matplotlib
```

Standard library only: `csv`, `math`, `random` (no extra ML packages).

## Usage

1. Place `packages.csv` and `cars.csv` in the same folder as `project_AI1.py`, or set the paths inside the script (see below).
2. Run:
   ```bash
   python project_AI1.py
   ```
3. Use the menu:
   - **1** — Read files and generate initial assignment.
   - **2** — Run Simulated Annealing and show resulting routes.
   - **3** — Run Genetic Algorithm and plot best assignment.
   - **4** — Exit.

**Note:** Load data (option 1) before running Simulated Annealing (2) or Genetic Algorithm (3).

## Configuring file paths

If your CSVs are not in the script’s directory, edit the paths in `main()` (option 1) and use the same paths for SA/GA. Example with relative paths:

```python
# Example: run from project folder
global_packages = read_file("packages.csv", max_weight=100.0, sort_by_priority=True)
global_vehicles = read_vehicles_file("cars.csv")
packages = read_packages("packages.csv")
vehicles = read_vehicles("cars.csv")
```

## Cost / fitness

- **Simulated Annealing:** Cost = total route distance + priority penalty (priority × position in route).
- **Genetic Algorithm:** Fitness = sum of (11 − priority) per delivered package − scaled distance − overload penalty.

## Outputs

- Console: iterations, cost/fitness, final package→vehicle assignment.
- Matplotlib: route plot (depot at (0,0), packages as points, one color per vehicle).


