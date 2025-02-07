import pandas as pd
import matplotlib.pyplot as plt

def load_and_prepare(file_path):
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df.sort_values("Date").reset_index(drop=True)

def get_closest_available_date(df, target_date):
    available_dates = df["Date"]
    closest_date = available_dates[available_dates <= target_date].max()
    return closest_date if pd.notna(closest_date) else available_dates.min()

def process_mixed_sma_strategy(msci_normal_path, msci_momentum_path, start_date: str, end_date: str, sma: int):
    df_normal = load_and_prepare(msci_normal_path)
    df_momentum = load_and_prepare(msci_momentum_path)
    
    # Compute SMA using MSCI Normal
    if sma > 0:
        df_normal["SMA"] = df_normal["Value"].rolling(window=sma).mean()
    else:
        df_normal["SMA"] = df_normal["Value"]  # If SMA is 0, just use the value itself
    
    # Ensure data within the selected time range
    closest_start_date = get_closest_available_date(df_normal, pd.to_datetime(start_date))
    closest_end_date = get_closest_available_date(df_normal, pd.to_datetime(end_date))
    df_normal = df_normal[(df_normal["Date"] >= closest_start_date) & (df_normal["Date"] <= closest_end_date)].reset_index(drop=True)
    
    closest_end_date_momentum = get_closest_available_date(df_momentum, pd.to_datetime(end_date))
    df_momentum = df_momentum[(df_momentum["Date"] >= closest_start_date) & (df_momentum["Date"] <= closest_end_date_momentum)].reset_index(drop=True)
    
    # Track capital
    capital = 0
    position = 10000 / df_momentum.iloc[0]["Value"]  # Always start with a buy
    last_signal = "Buy"
    
    for i in range(1, len(df_normal)):
        current_price_normal = df_normal.loc[i, "Value"]
        sma_value = df_normal.loc[i, "SMA"]
        current_date = df_normal.loc[i, "Date"]
        
        if pd.notna(sma_value):
            # Find the closest date in the MSCI Momentum dataset
            closest_momentum_row = df_momentum.iloc[(df_momentum["Date"] - current_date).abs().argsort()[:1]]
            if closest_momentum_row.empty:
                continue  # Skip if no close date exists
            
            current_price_momentum = closest_momentum_row["Value"].values[0]
            
            if last_signal == "Buy" and current_price_normal <= 0.97 * sma_value:
                # Sell MSCI Momentum
                capital = position * current_price_momentum
                position = 0
                last_signal = "Sell"
            elif last_signal == "Sell" and current_price_normal > 1.01 * sma_value:
                # Buy MSCI Momentum
                position = capital / current_price_momentum
                capital = 0
                last_signal = "Buy"
    
    # Final value
    final_value = capital + (position * df_momentum.iloc[-1]["Value"] if position > 0 else 0)
    return final_value

def calculate_buy_and_hold(msci_momentum_path, start_date: str, end_date: str):
    df = load_and_prepare(msci_momentum_path)
    closest_start_date = get_closest_available_date(df, pd.to_datetime(start_date))
    closest_end_date = get_closest_available_date(df, pd.to_datetime(end_date))
    df = df[(df["Date"] >= closest_start_date) & (df["Date"] <= closest_end_date)].reset_index(drop=True)
    buy_and_hold_position = 10000 / df.iloc[0]["Value"]
    buy_and_hold_value = buy_and_hold_position * df.iloc[-1]["Value"]
    return buy_and_hold_value

# File paths
msci_normal_path = "Msci_Daily.csv"
msci_momentum_path = "Msci_mom_Daily.csv"
start_date = '2014-01-31'
end_date = '2024-12-31'

# Test different SMA values
sma_values = list(range(50, 250, 5))  # Include 0 for buy-and-hold comparison
strategy_results = [process_mixed_sma_strategy(msci_normal_path, msci_momentum_path, start_date, end_date, sma) for sma in sma_values]

# Compute Buy-and-Hold strategy
buy_and_hold_value = calculate_buy_and_hold(msci_momentum_path, start_date, end_date)

# Find best SMA
best_sma = sma_values[strategy_results.index(max(strategy_results))]

# Plot results
plt.figure(figsize=(12, 6))
plt.plot(sma_values, strategy_results, marker='o', linestyle='-', label='Strategy Performance')
plt.axhline(y=buy_and_hold_value, color='r', linestyle='--', label='Buy and Hold')
plt.axvline(x=best_sma, color='g', linestyle='--', label=f'Best SMA: {best_sma}')
plt.xlabel("SMA Window")
plt.ylabel("Final Capital")
plt.title("SMA Strategy Performance using MSCI Normal Signals on MSCI Momentum")
plt.legend()
plt.grid(True)
plt.show()

print(f"Best SMA: {best_sma}, Final Capital: {max(strategy_results):.2f}")
print(f"Buy-and-Hold Final Capital: {buy_and_hold_value:.2f}")
