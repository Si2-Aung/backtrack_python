import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
def load_and_prepare(file_path):
    df = pd.read_excel(file_path, index_col=0, parse_dates=True)
    df = df.sort_values(by='Date').reset_index()
    return df

# Get closest available trading date
def get_closest_available_date(df, target_date):
    available_dates = df['Date']
    closest_date = available_dates[available_dates <= target_date].max()
    return closest_date if pd.notna(closest_date) else available_dates.min()

# Compute SMA
def calculate_sma(df, column='Spy', sma_window=200):
    df['SMA'] = df[column].rolling(window=sma_window, min_periods=sma_window).mean()
    return df[df['SMA'].notna()]  # Start only after SMA is available

# Strategy execution
def execute_strategy(df_spy, df_2spy, start_date, end_date, sma_window=200, initial_capital=1000, monthly_investment=100):
    df_spy = calculate_sma(df_spy, column='Spy', sma_window=sma_window)
    
    # Ensure valid start and end dates
    start_date = get_closest_available_date(df_spy, pd.to_datetime(start_date))
    end_date = get_closest_available_date(df_spy, pd.to_datetime(end_date))
    
    df_spy = df_spy[(df_spy['Date'] >= start_date) & (df_spy['Date'] <= end_date)].reset_index(drop=True)
    df_2spy = df_2spy[(df_2spy['Date'] >= start_date) & (df_2spy['Date'] <= end_date)].reset_index(drop=True)
    
    capital = 0
    position = initial_capital / df_2spy.iloc[0]['2Spy']  # Initial buy
    last_signal = "Buy"
    portfolio_values = []
    
    # Ensure Date is set as index before resampling
    df_spy = df_spy.set_index('Date')
    monthly_dates = df_spy.resample('MS').ffill().index
    df_spy = df_spy.reset_index()
    
    for date in monthly_dates:
        if date not in df_spy['Date'].values:
            continue
        spy_value = df_spy.loc[df_spy['Date'] == date, 'Spy'].values[0]
        sma_value = df_spy.loc[df_spy['Date'] == date, 'SMA'].values[0]
        
        closest_2spy_row = df_2spy.iloc[(df_2spy['Date'] - date).abs().argsort()[:1]]
        if closest_2spy_row.empty:
            continue
        
        price_2spy = closest_2spy_row['2Spy'].values[0]
        
        if last_signal == "Buy" and spy_value <= 0.98 * sma_value:
            capital = position * price_2spy  # Sell all
            position = 0
            last_signal = "Sell"
        elif last_signal == "Sell" and spy_value > 1.01 * sma_value:
            position = capital / price_2spy  # Buy back
            capital = 0
            last_signal = "Buy"
        
        capital -= monthly_investment
        position += monthly_investment / price_2spy
        portfolio_values.append(capital + position * price_2spy)
    
    final_value = capital + position * df_2spy.iloc[-1]['2Spy']
    return final_value, portfolio_values

# Buy-and-Hold for SPY
def calculate_buy_and_hold(df_2spy, start_date, end_date, initial_capital=1000):
    start_date = get_closest_available_date(df_2spy, pd.to_datetime(start_date))
    end_date = get_closest_available_date(df_2spy, pd.to_datetime(end_date))
    df_2spy = df_2spy[(df_2spy['Date'] >= start_date) & (df_2spy['Date'] <= end_date)].reset_index(drop=True)
    position = initial_capital / df_2spy.iloc[0]['2Spy']
    buy_and_hold_value = position * df_2spy.iloc[-1]['2Spy']
    return buy_and_hold_value

# File paths
spy_path = 'Spys.xlsx'
df_spy = load_and_prepare(spy_path)
df_2spy = df_spy.copy()
df_2spy.rename(columns={'2Spy': '2Spy'}, inplace=True)

start_date = '2019-01-30'
end_date = '2025-02-14'

# Test different SMA values
sma_values = list(range(50, 250, 5))
strategy_results = [execute_strategy(df_spy, df_2spy, start_date, end_date, sma)[0] for sma in sma_values]

# Compute Buy-and-Hold strategy
buy_and_hold_value = calculate_buy_and_hold(df_2spy, start_date, end_date)

# Find best SMA
best_sma = sma_values[strategy_results.index(max(strategy_results))]

# Plot results
plt.figure(figsize=(12, 6))
plt.plot(sma_values, strategy_results, marker='o', linestyle='-', label='Strategy Performance')
plt.axhline(y=buy_and_hold_value, color='r', linestyle='--', label='Buy and Hold')
plt.axvline(x=best_sma, color='g', linestyle='--', label=f'Best SMA: {best_sma}')
plt.xlabel("SMA Window")
plt.ylabel("Final Capital")
plt.title("SMA Strategy Performance using SPY Signals on 2SPY")
plt.legend()
plt.grid(True)
plt.show()

print(f"Best SMA: {best_sma}, Final Capital: {max(strategy_results):.2f}")
print(f"Buy-and-Hold Final Capital: {buy_and_hold_value:.2f}")
