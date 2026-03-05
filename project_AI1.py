import csv
import math
import random
import matplotlib.pyplot as plt

cars_num = 0
global_packages = []
global_vehicles = []
global_initial_state = {}
global_ga_packages = []  # Package objects for Genetic Algorithm
global_ga_vehicles = []  # Vehicle objects for Genetic Algorithm

def generate_initial_state(packages, vehicles):
    state = {vehicle['id']: [] for vehicle in vehicles}
    capacities = {vehicle['id']: vehicle['capacity'] for vehicle in vehicles}
    shuffled_packages = packages.copy()
    random.shuffle(shuffled_packages)
    for package in shuffled_packages:
        pkg_id = package['id']
        pkg_weight = package['weight']
        random.shuffle(vehicles)
        for vehicle in vehicles:
            vid = vehicle['id']
            if capacities[vid] >= pkg_weight:
                state[vid].append(pkg_id)
                capacities[vid] -= pkg_weight
                break
        else:
            print(f"Warning: Package {pkg_id} couldn't be assigned (too heavy!)")
    return state

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def read_file(filename, max_weight=None, as_dict=False, sort_by_priority=False):
    packages = []
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                package = {
                    'id': row['id'],
                    'x': float(row['x']),
                    'y': float(row['y']),
                    'weight': float(row['weight']),
                    'priority': int(row['priority'])
                }
                if max_weight is not None and package['weight'] > max_weight:
                    continue
                packages.append(package)
        if sort_by_priority:
            packages.sort(key=lambda p: p['priority'])
        if as_dict:
            return {p['id']: p for p in packages}
        return packages
    except Exception as e:
        print(f"Error reading package file: {e}")
        return {} if as_dict else []

def read_vehicles_file(filename):
    vehicles = []
    global cars_num
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cars_num += 1
                vehicle = {
                    'id': row['id'],
                    'capacity': float(row['capacity'])
                }
                vehicles.append(vehicle)
        return vehicles
    except Exception as e:
        print(f"Error reading vehicle file: {e}")
        return []

def compute_cost(state, packages_dict, vehicles):
    shop_x, shop_y = 0, 0
    total_cost = 0
    for vehicle in vehicles:
        vid = vehicle['id']
        route = state.get(vid, [])
        if not route:
            continue
        path = [(shop_x, shop_y)] + [(packages_dict[pid]['x'], packages_dict[pid]['y']) for pid in route]
        route_cost = 0
        for i in range(len(path) - 1):
            pid = route[i] if i < len(route) - 2 else None
            dist = euclidean_distance(*path[i], *path[i+1])
            if pid:
                p = packages_dict[pid]
                priority_penalty = p['priority'] * i
                total_cost += priority_penalty
            else:
                route_cost += dist
        total_cost += route_cost
    return total_cost

def get_random_neighbor(state, packages_dict, vehicles_dict):
    import copy
    neighbor = copy.deepcopy(state)
    from_vid = random.choice(list(neighbor.keys()))
    if not neighbor[from_vid]:
        return neighbor
    package_id = random.choice(neighbor[from_vid])
    package = packages_dict[package_id]
    neighbor[from_vid].remove(package_id)
    for to_vid, to_vehicle in vehicles_dict.items():
        if to_vid == from_vid:
            continue
        current_weight = sum(packages_dict[pid]['weight'] for pid in neighbor[to_vid])
        if current_weight + package['weight'] <= to_vehicle['capacity']:
            neighbor[to_vid].append(package_id)
            return neighbor
    neighbor[from_vid].append(package_id)
    return neighbor

def simulated_annealing(packages, vehicles, initial_state, max_iter=10000, init_temp=1000, cooling_rate=0.95, stop_temp=1):
    packages_dict = {p['id']: p for p in packages}
    vehicles_dict = {v['id']: v for v in vehicles}
    current = initial_state
    current_cost = compute_cost(current, packages_dict, vehicles)
    best = current
    best_cost = current_cost
    temperature = init_temp
    for t in range(1, max_iter + 1):
        if temperature < stop_temp:
            break
        neighbor = get_random_neighbor(current, packages_dict, vehicles_dict)
        neighbor_cost = compute_cost(neighbor, packages_dict, vehicles)
        print(f"Iteration {t}: Cost = {neighbor_cost}, State = {neighbor}")


        delta_e = current_cost - neighbor_cost
        if delta_e > 0 or random.random() < math.exp(delta_e / temperature):
            current = neighbor
            current_cost = neighbor_cost
            if neighbor_cost < best_cost:
                best = neighbor
                best_cost = neighbor_cost
        temperature *= cooling_rate
    return best, best_cost

def visualize_solution(state, packages_dict, vehicles):
    plt.figure(figsize=(10, 8))
    colors = plt.colormaps.get_cmap('tab10')
    for i, vehicle in enumerate(vehicles):
        vid = vehicle['id']
        route = state.get(vid, [])
        if not route:
            continue
        path = [(0, 0)] + [(packages_dict[pid]['x'], packages_dict[pid]['y']) for pid in route] 
        x_coords = [point[0] for point in path]
        y_coords = [point[1] for point in path]
        plt.plot(x_coords, y_coords, marker='o', label=f'Vehicle {vid}', color=colors(i % 10))
        for pid in route:
            px, py = packages_dict[pid]['x'], packages_dict[pid]['y']
            plt.text(px, py, f'{pid}', fontsize=9)
    plt.plot(0, 0, marker='s', color='black', markersize=10, label='Shop (0,0)')
    plt.title("Package Delivery Routes")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.show()

def mainMenu():
    print("\nWelcome to our Optimization Strategies for Local Package Delivery Operations :) ")
    print("1. Read files")
    print("2. Simulated Annealing")
    print("3. Genetic algorithms")
    print("4. Exit")

def main():
    global global_packages, global_vehicles, global_initial_state, global_ga_packages, global_ga_vehicles
    while True:
        mainMenu()
        choice = input("Enter your choice: ")
        if choice == '1':
            # Use paths relative to script location (packages.csv, cars.csv in same folder)
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            packages_path = os.path.join(base_dir, "packages.csv")
            cars_path = os.path.join(base_dir, "cars.csv")
            global_packages = read_file(packages_path, max_weight=100.0, sort_by_priority=True)
            global_vehicles = read_vehicles_file(cars_path)
            packages = read_packages(packages_path)
            vehicles = read_vehicles(cars_path)

            print("\n🚚 Vehicles:")
            for v in global_vehicles:
                print(v)
            print("\n📦 Packages:")
            for p in global_packages:
                print(p)
            print("\nNumber of cars:", cars_num)
            global_initial_state = generate_initial_state(global_packages, global_vehicles)
            global_ga_packages = packages
            global_ga_vehicles = vehicles
            print("Initial State:", global_initial_state)
        elif choice == '2':
            if not global_initial_state:
                print("Please load the data first (Option 1).")
                continue
            result_state, cost = simulated_annealing(global_packages, global_vehicles, global_initial_state,
                                                     max_iter=1000, init_temp=1000, cooling_rate=0.95, stop_temp=1)
            print("\n✅ Simulated Annealing completed.")
            print("Resulting Cost:", cost)
            print("Resulting Assignment:")
            for k, v in result_state.items():
                print(f"Vehicle {k}: {v}")
            packages_dict = {p['id']: p for p in global_packages}
            visualize_solution(result_state, packages_dict, global_vehicles)
        elif choice == '3':
            if not global_ga_packages or not global_ga_vehicles:
                print("Please load the data first (Option 1).")
                continue
            best_assignment = genetic_algorithm(global_ga_packages, global_ga_vehicles)
            plot_routes(global_ga_packages, global_ga_vehicles, best_assignment)
        elif choice == '4':
            print("Exiting.")
            break
        else:
            print("Invalid choice, please enter a valid option.")

class Package:
    def __init__(self, id, x, y, weight, priority):
        self.id = id
        self.x = x
        self.y = y
        self.weight = weight
        self.priority = priority

class Vehicle:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity

# ==== CSV Readers ====

def read_packages(file_path):
    packages = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            packages.append(Package(
                int(row['id']),
                float(row['x']),
                float(row['y']),
                float(row['weight']),
                int(row['priority'])
            ))
    return packages

def read_vehicles(file_path):
    vehicles = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Vehicle CSV Columns:", reader.fieldnames)  # Debug: Print CSV headers
        for row in reader:
            vehicles.append(Vehicle(
                int(row['id']),
                float(row['capacity'])
            ))
    return vehicles

# ==== Genetic Algorithm ====

def calculate_distance(p1, p2=(0, 0)):
    return math.sqrt((p1.x - p2[0]) ** 2 + (p1.y - p2[1]) ** 2)

def fitness(individual, packages, vehicles):
    vehicle_loads = [0] * len(vehicles)
    vehicle_priorities = [0] * len(vehicles)
    vehicle_distance = [0] * len(vehicles)
    penalty = 0
    left_out_packages = []  # Track packages that cannot be assigned

    for i, vehicle_idx in enumerate(individual):
        pkg = packages[i]
        vehicle = vehicles[vehicle_idx]

        # Check if the package fits in the vehicle
        if vehicle_loads[vehicle_idx] + pkg.weight <= vehicle.capacity:
            vehicle_loads[vehicle_idx] += pkg.weight
            vehicle_priorities[vehicle_idx] += (11 - pkg.priority)  # Higher reward for higher priority
            vehicle_distance[vehicle_idx] += calculate_distance(pkg)
        else:
            # If the package does not fit, add it to the list of left-out packages
            left_out_packages.append(pkg)
            individual[i] = -1  # Assign -1 for packages that are not assigned to any vehicle

    # Calculate penalties for overloading
    for idx, load in enumerate(vehicle_loads):
        overload = load - vehicles[idx].capacity
        if overload > 0:
            penalty += overload * 20  # Increase penalty for exceeding capacity

    # Compute total fitness: priorities - scaled distance - penalty
    priority_score = sum(vehicle_priorities)
    distance_penalty = sum(d / 50 for d in vehicle_distance)  # Scale distance down
    total_fitness = priority_score - distance_penalty - penalty

    # Print left-out packages for debugging
    #print(f"Left-out packages: {[pkg.id for pkg in left_out_packages]}")

    return total_fitness

def create_individual(num_packages, num_vehicles):
    return [random.randint(0, num_vehicles - 1) for _ in range(num_packages)]

def mutate(individual, num_vehicles, mutation_rate=0.01):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            original = individual[i]
            individual[i] = random.randint(0, num_vehicles - 1)
            #print(f"Mutated gene {i}: {original} -> {individual[i]}")

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 2)
    child = parent1[:point] + parent2[point:]
    #print(f"Crossover at {point}")
    return child

def genetic_algorithm(packages, vehicles, population_size=70, generations=500):
    population = [create_individual(len(packages), len(vehicles)) for _ in range(population_size)]

    for gen in range(generations):
        fitness_scores = [fitness(ind, packages, vehicles) for ind in population]
        best_fitness = max(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        min_fitness = min(fitness_scores)

        print(f"Gen {gen}: max={best_fitness} min={min_fitness} avg={avg_fitness:.2f}")
        #print("Sample individual:", population[fitness_scores.index(best_fitness)])

        # Selection (top 20%)
        sorted_population = [ind for _, ind in sorted(zip(fitness_scores, population), reverse=True)]
        survivors = sorted_population[:population_size // 5]

        # Create next gen
        next_gen = survivors.copy()
        while len(next_gen) < population_size:
            p1, p2 = random.sample(survivors, 2)
            child = crossover(p1, p2)
            mutate(child, len(vehicles))
            next_gen.append(child)

        population = next_gen

    # Final best
    best = max(population, key=lambda ind: fitness(ind, packages, vehicles))
    print("\nBest assignment of packages to vehicles (with some packages left out):")
    for i, vehicle_id in enumerate(best):
        if vehicle_id != -1:  # Skip packages left out (id == -1)
            print(f"Package {packages[i].id} -> Vehicle {vehicles[vehicle_id].id}")
        else:
            print(f"Package {packages[i].id} is left out.")

    return best

# ==== Plotting ====

def plot_routes(packages, vehicles, assignment):
    plt.figure(figsize=(10, 8))

    # Plot vehicles starting from (0, 0)
    for vehicle_id in range(len(vehicles)):
        vehicle = vehicles[vehicle_id]
        vehicle_assigned_packages = [pkg for i, pkg in enumerate(packages) if assignment[i] == vehicle_id]
        # Starting point at (0, 0)
        route_x = [0]
        route_y = [0]
        
        for pkg in vehicle_assigned_packages:
            route_x.append(pkg.x)
            route_y.append(pkg.y)
        
        plt.plot(route_x, route_y, marker='o', label=f'Vehicle {vehicle_id + 1}')

    # Plot packages as points
    for pkg in packages:
        plt.scatter(pkg.x, pkg.y, color='red', zorder=5)
        plt.text(pkg.x + 1, pkg.y + 1, f'Pkg {pkg.id}', fontsize=9, color='black')

    plt.xlim(-10, max(pkg.x for pkg in packages) + 10)
    plt.ylim(-10, max(pkg.y for pkg in packages) + 10)
    plt.title('Vehicle Routes and Package Assignments')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
