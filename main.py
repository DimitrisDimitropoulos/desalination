import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import CubicSpline
from dats.dats import pv_pr, v_wind

# cost of installation of wind turbine
c_wind: int = 1340  # [euro/kW]
# cost of installation of solar panel
c_solar: int = 800  # [euro/kWp] peak power
# capacity of reverse osmosis desalination plant
q_ro = 19200  # [m3/day]
# specific energy consumption of reverse osmosis plant
sec_ro: float = 3.0  # [kWh/m3]
# yearly needed water volume
q_water: float = 11.7 * 10**6  # [m3/year]
# capex of desalination plant
c_ro: float = 900  # [euro/m3*day]
# percentage per month of the total water consumption in %
wtr_cons_mnth: list[int] = [6, 7, 7, 8, 9, 11, 12, 11, 9, 7, 7, 6]
# number of desalination plants
n_ro: int = 2
# number of wind turbines
n_wind: int = 200
# peak power of solar panels
p_solar: float = 0.9  # [kWp]
# number of solar panels
n_solar: int = 1000


def calculate_tank_capacity(
    wtr_cons_mnth: list[int], q_water: float, extra: float
) -> float:
    """
    Calculate the capacity of the tank to keep water.
    The capacity must be at least the volume that is consumed for one week of the toughest month.
    Parameters:
    wtr_cons_mnth (list[int]): The percentage per month of the total water consumption.
    q_water (float): The yearly needed water volume in cubic meters.
    Returns:
    float: The required tank capacity in cubic meters.
    """
    # Number of days in each month
    days_in_month: list[int] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # Calculate the monthly water consumption
    monthly_consumption: list[float] = [
        (percentage / 100) * q_water for percentage in wtr_cons_mnth
    ]
    # Calculate the daily water consumption for each month
    daily_consumption: list[float] = [
        monthly / days for monthly, days in zip(monthly_consumption, days_in_month)
    ]
    # Find the toughest month (the month with the highest daily consumption)
    toughest_month_index: int = daily_consumption.index(max(daily_consumption))
    # Calculate the weekly water consumption for the toughest month
    weekly_consumption: float = daily_consumption[toughest_month_index] * 7
    return weekly_consumption + extra


tank_capacity: float = calculate_tank_capacity(wtr_cons_mnth, q_water, 700000)
# print it in million cubic meters
print(f"Tank capacity: {tank_capacity / 10**6} million cubic meters")
# Create a DataFrame
df = pd.DataFrame({"pv_pr": pv_pr, "v_wind": v_wind})
# Calculate mean and standard deviation of v_wind
mean_v_wind: float = float(df["v_wind"].mean())
std_v_wind: float = float(df["v_wind"].std())
print(f"Mean of v_wind: {mean_v_wind}")
print(f"Standard deviation of v_wind: {std_v_wind}")


def plot_v_wind_occurrences(data: pd.Series) -> None:
    """
    Plot the occurrences of v_wind.
    Parameters:
    data (pd.Series): The data series to plot.
    """
    plt.hist(data, bins=10, edgecolor="black")
    plt.title("Occurrences of v_wind")
    plt.xlabel("v_wind")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()


# Wind turbine power curve
wind_speed: list[int] = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
]
power: list[int] = [
    0,
    0,
    0,
    4,
    27,
    66,
    120,
    197,
    295,
    421,
    575,
    736,
    866,
    943,
    987,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
]


def wind_power_spline(speed: float) -> float:
    """
    Calculate the power in kW for a given wind speed using a cubic spline.
    Parameters:
        speed (float): The speed of wind in m/s.
    Returns:
        float: The power in kW.
    """
    # If speed is greater than the maximum wind speed in the dataset, return 0
    if speed > max(wind_speed):
        return 0
    # Create a cubic spline interpolation
    spline = CubicSpline(wind_speed, power)
    # Calculate the power at the given speed
    power_output = float(spline(speed))
    # Check if the power is negative and return 0 if so
    if power_output < 0:
        return 0
    return power_output


# Add a new column to the DataFrame that calculates the power using the spline function
df["power_wt"] = df["v_wind"].apply(wind_power_spline)
df["power_wt"] = df["power_wt"] * n_wind
# Calculate the power generated by the solar panels by multiplying the peak
# power by the number of panels for every item of the pv_pr collumn
df["power_solar"] = df["pv_pr"].apply(lambda x: x * n_solar * p_solar)


def plot_power_vs_wind_speed(
    df: pd.DataFrame, wind_speed_col: str, power_col: str
) -> None:
    """
    Plot the power against wind speed as a scatter plot.
    Parameters:
    df (pd.DataFrame): The DataFrame containing wind speed and power data.
    wind_speed_col (str): The column name for wind speed.
    power_col (str): The column name for power.
    """
    plt.scatter(df[wind_speed_col], df[power_col], label="Power vs Wind Speed")
    plt.title("Power vs Wind Speed")
    plt.xlabel("Wind Speed (m/s)")
    plt.ylabel("Power (kW)")
    plt.grid(True)
    plt.legend()
    plt.show()


# plot_power_vs_wind_speed(df, "v_wind", "power_wt")
# calculate the hourly water from desalination
q_ro_hourly: float = q_ro / 24
# calculate the hourly energy needed for desalination
e_ro_hourly: float = q_ro_hourly * sec_ro  # [kW]
# fill a column in the dataframe with the hourly energy needed for
# desalination, with the same amount of rows as the dataframe
df["e_ro_hourly"] = e_ro_hourly


def simulate_tank_operations(
    df: pd.DataFrame,
    tank_capacity: float,
    q_water: float,
    wtr_cons_mnth: list[int],
    q_ro_hourly: float,
    e_ro_hourly: float,
    n_ro: int,
    n_wind: int,
) -> pd.DataFrame:
    """
    Simulate the tank operations over time.
    Parameters:
    df (pd.DataFrame): DataFrame containing wind and solar power data.
    tank_capacity (float): Maximum capacity of the tank in cubic meters.
    q_water (float): Yearly needed water volume in cubic meters.
    wtr_cons_mnth (list[int]): Percentage of total water consumption per month.
    q_ro_hourly (float): Hourly water production per desalination plant.
    e_ro_hourly (float): Hourly energy needed per desalination plant.
    n_ro (int): Total number of desalination plants.
    n_wind (int): Total number of wind turbines.
    Returns:
    pd.DataFrame: DataFrame with updated tank levels and simulation results.
    """
    days_in_month: list[int] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # Initialize tank level
    tank_level: float = tank_capacity * 0.05
    # Prepare lists to store simulation results
    tank_levels: list[float] = []
    water_produced: list[float] = []
    water_consumed: list[float] = []
    plants_operating: list[int] = []
    # Create a date range corresponding to the DataFrame length
    start_date = pd.Timestamp("2023-01-01 00:00:00")
    date_range = pd.date_range(start=start_date, periods=len(df), freq="H")
    df = df.copy()
    df["datetime"] = date_range
    df["month"] = df["datetime"].dt.month
    # Calculate monthly, daily, and hourly water consumption
    monthly_consumption: list[float] = [
        (percentage / 100) * q_water for percentage in wtr_cons_mnth
    ]
    daily_consumption: list[float] = [
        monthly / days for monthly, days in zip(monthly_consumption, days_in_month)
    ]
    hourly_consumption: list[float] = [daily / 24 for daily in daily_consumption]
    # Map month to hourly consumption
    month_to_hourly_consumption: dict[int, float] = {
        month + 1: hourly for month, hourly in enumerate(hourly_consumption)
    }
    # Iterate over each hour in the DataFrame
    for index, row in df.iterrows():
        month: int = row["month"]
        power_generated: float = (
            (row["power_wt"]) + row["power_solar"]
        )  # Total power generated [kW]
        water_needed: float = month_to_hourly_consumption[
            month
        ]  # Hourly water needed [m³]
        # Determine number of plants that can operate
        max_plants_operating: int = min(n_ro, int(power_generated // e_ro_hourly))
        plants_in_operation: int = max_plants_operating
        # Calculate water production and energy used
        water_output: float = plants_in_operation * q_ro_hourly  # [m³/h]
        energy_used: float = plants_in_operation * e_ro_hourly  # [kW]
        # Update tank level: Add water produced, then subtract water consumed
        tank_level += water_output
        if tank_level > tank_capacity:
            tank_level = tank_capacity  # Tank is full
        tank_level -= water_needed
        if tank_level < 0:
            tank_level = 0  # Tank is empty
        # Record the simulation data
        tank_levels.append(tank_level)
        water_produced.append(water_output)
        water_consumed.append(water_needed)
        plants_operating.append(plants_in_operation)
    # Add simulation results to DataFrame
    df["tank_level"] = tank_levels
    df["water_produced"] = water_produced
    df["water_consumed"] = water_consumed
    df["plants_operating"] = plants_operating
    return df


# Assuming 'df' already has 'power_solar' calculated
df_results = simulate_tank_operations(
    df=df,
    tank_capacity=tank_capacity,
    q_water=q_water,
    wtr_cons_mnth=wtr_cons_mnth,
    q_ro_hourly=q_ro_hourly,
    e_ro_hourly=e_ro_hourly,
    n_ro=n_ro,
    n_wind=n_wind,
)

# # Plot the tank level over time
# plt.figure(figsize=(12, 6))
# plt.plot(df_results["datetime"], df_results["tank_level"], label="Tank Level")
# plt.xlabel("Date")
# plt.ylabel("Tank Level (m³)")
# plt.title("Tank Level Over Time")
# plt.legend()
# plt.grid(True)
# plt.show()

df_results.to_csv("./out/df_results.csv", index=False)

"""
Cost analysis
"""


def calculate_tank_cost(volume: float) -> float:
    """
    Calculate the cost of a tank based on an exponential law of the volume with two parameters.
    Parameters:
        volume (float): The volume of the tank.
        a (float): The scaling parameter.
        b (float): The exponent parameter.
    Returns:
        float: The cost of the tank.
    """
    lambda_: float = 1000
    alpha_: float = 0.6
    cost: float = lambda_ * volume**alpha_
    return cost


tank_cost: float = calculate_tank_cost(tank_capacity)

# number of years to take into account
N: int = 20  # [years]
# discount rate
i: float = 0.06  # [-]
# opex as a percentage of capex
opex: float = 0.03  # [-]


def calculate_annuity_factor(i: float, N: int) -> float:
    """
    Calculate the annuity factor R based on the interest rate and number of periods.
    Parameters:
        i (float): The interest rate per period.
        N (int): The number of periods.
    Returns:
        float: The annuity factor R.
    """
    return i / (1 - (1 + i) ** (-N))


R: float = calculate_annuity_factor(i, N)


def calculate_capex(
    c_wind: int,
    n_wind: int,
    c_solar: int,
    n_solar: int,
    p_solar: float,
    q_ro: float,
    n_ro: int,
    c_ro: float,
    tank_cost: float,
) -> tuple[float, float, float, float, float]:
    """
    Calculate the CAPEX based on the costs of wind turbines, solar panels, and desalination plants, and the provided tank cost.
    Also, calculate the percentage of cost for each part.
    Parameters:
        c_wind (int): Cost of installation of wind turbine [euro/kW].
        n_wind (int): Number of wind turbines.
        c_solar (int): Cost of installation of solar panel [euro/kWp].
        n_solar (int): Number of solar panels.
        p_solar (float): Peak power of solar panels [kWp].
        q_ro (float): Capacity of reverse osmosis desalination plant [m3/day].
        n_ro (int): Number of desalination plants.
        c_ro (float): Capex of desalination plant [euro/m3*day].
        tank_cost (float): The cost of the tank.
    Returns:
        tuple: Total CAPEX and the percentage of cost for wind, solar, desalination, and tank.
    """
    # Calculate the cost of wind turbines
    cost_wind: float = c_wind * n_wind
    # Calculate the cost of solar panels
    cost_solar: float = c_solar * n_solar * p_solar
    # Calculate the cost of desalination plants
    cost_desalination: float = q_ro * n_ro * c_ro
    # Sum the costs to get the total CAPEX
    total_capex: float = cost_wind + cost_solar + cost_desalination + tank_cost
    # Calculate the percentage of each cost
    wind_percentage: float = (cost_wind / total_capex) * 100
    solar_percentage: float = (cost_solar / total_capex) * 100
    desalination_percentage: float = (cost_desalination / total_capex) * 100
    tank_percentage: float = (tank_cost / total_capex) * 100
    return (
        total_capex,
        wind_percentage,
        solar_percentage,
        desalination_percentage,
        tank_percentage,
    )


# Example usage
(
    total_capex,
    wind_percentage,
    solar_percentage,
    desalination_percentage,
    tank_percentage,
) = calculate_capex(
    c_wind=c_wind,
    n_wind=n_wind,
    c_solar=c_solar,
    n_solar=n_solar,
    p_solar=p_solar,
    q_ro=q_ro,
    n_ro=n_ro,
    c_ro=c_ro,
    tank_cost=tank_cost,
)

print(f"Total CAPEX: {total_capex/10**6:.2f} million euros")
print(f"Wind CAPEX: {wind_percentage:.2f}%")
print(f"Solar CAPEX: {solar_percentage:.2f}%")
print(f"Desalination CAPEX: {desalination_percentage:.2f}%")
print(f"Tank CAPEX: {tank_percentage:.2f}%")

# Calculate the OPEX based on the CAPEX
opex_cost: float = opex * total_capex

## Calculate the LCOW
lcow: float = (total_capex * R + opex_cost) / (q_water)  # [euro/m3]
print(f"LCOW: {lcow:.2f} euro/m3")
