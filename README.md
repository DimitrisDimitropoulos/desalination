# Water Production Cost Analysis Simulation Software

This project simulates the cost of producing water using renewable energy
sources. The analysis includes calculating the initial investment cost (CAPEX),
operational cost (OPEX), and the levelized cost of water (LCOW). The project
also simulates the operation of a water tank and evaluates different
configurations of wind turbines and solar panels to find viable solutions.

## Features

-   **Full-Scale Yearly Simulation**: Simulates the operation of a water production system over an entire year, taking into account daily and seasonal variations in water consumption and renewable energy production.
-   **Parallel Processing**: Utilizes parallel processing to evaluate multiple configurations of wind turbines and solar panels simultaneously, significantly reducing computation time.
-   **Cost Analysis**: Calculates the initial investment cost (CAPEX), operational cost (OPEX), and the levelized cost of water (LCOW) for different system configurations.
-   **Visualization**: Generates plots to visualize the tank level over time, the distribution of CAPEX, and the frequency of plants operating.


![tank](https://github.com/user-attachments/assets/2d8bf0e8-1855-464f-af53-ba925d8fc557)

![better](https://github.com/user-attachments/assets/9faf5812-1bda-49c6-a267-814592032034)

## Requirements

-   Python 3.x
-   pandas
-   matplotlib
-   scipy

## Usage

1. Run the main script to perform the analysis and generate plots:

    ```sh
    python main.py
    ```

2. The results will be saved in the `./out` directory:
    - `df_results.csv`: Simulation results of tank operations.
    - `viable_solutions_4.csv`: Viable solutions for different configurations of wind turbines and solar panels.

## Simulation Details

### Full-Scale Yearly Simulation

The software simulates the operation of a water production system over an entire year. It takes into account the following factors:

-   **Daily and Seasonal Variations**: The software models daily and seasonal variations in water consumption and renewable energy production.
-   **Tank Operations**: The simulation tracks the water level in the tank, ensuring that it meets the demand while considering the production from desalination plants powered by wind turbines and solar panels.
-   **Energy Production**: The power output from wind turbines is calculated using a cubic spline interpolation of the wind speed data, while the power output from solar panels is based on the photovoltaic production ratio.

### Parallel Processing

To efficiently evaluate multiple configurations of wind turbines and solar panels, the software uses parallel processing. This is achieved using the `concurrent.futures` module, which allows the software to run multiple simulations concurrently. The key steps are:

1. **Generate Combinations**: Generate all possible combinations of wind turbine counts and solar panel capacities to evaluate.
2. **Submit Tasks**: Submit each combination as a separate task to a process pool executor.
3. **Collect Results**: Collect the results from each task and identify viable solutions based on the minimum tank level and CAPEX.

### Key Functions

-   `calculate_tank_capacity()`: Calculates the required tank capacity based on the toughest month's water consumption.
-   `wind_power_spline()`: Calculates the power output of wind turbines using a cubic spline interpolation.
-   `simulate_tank_operations()`: Simulates the operation of the water tank over time, tracking the tank level, water produced, and plants operating.
-   `calculate_capex()`: Calculates the initial investment cost (CAPEX) and its distribution among different components.
-   `find_viable_solutions_parallel()`: Finds viable solutions for different configurations of wind turbines and solar panels in parallel.

### Plots

-   **Tank Level Over Time**: Visualizes the water level in the tank throughout the year.
-   **CAPEX Distribution**: Displays the distribution of the initial investment cost among different components.
-   **Frequency of Plants Operating**: Shows the frequency distribution of the number of desalination plants operating.

## License

See `LICENSE` file.
