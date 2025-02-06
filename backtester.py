import pandas as pd

def calculate_buy_and_hold(file_path, date: str):
    # CSV-Datei laden
    df = pd.read_csv(file_path)

    # Sicherstellen, dass die Spalten korrekt als Datum und numerischer Wert interpretiert werden
    df["Date"] = pd.to_datetime(df["Date"])  # Datumskonvertierung
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")  # Indexwerte als numerische Werte

    # Buy-and-hold Vergleich
    buy_and_hold_position = 10000 /df[df["Date"] >= date].iloc[0]["Value"]
    print(f"Buy and Hold: Buy at {df[df['Date'] >= date].iloc[0]['Value']:.2f}, Position: {buy_and_hold_position:.2f}")
    buy_and_hold_value = buy_and_hold_position * df.loc[len(df) - 1, "Value"]
    return buy_and_hold_value


def process_momentum_csv(file_path, date: str, sma: int):
    # CSV-Datei laden
    df = pd.read_csv(file_path)
    
    # Sicherstellen, dass die Spalten korrekt als Datum und numerischer Wert interpretiert werden
    df["Date"] = pd.to_datetime(df["Date"])  # Datumskonvertierung
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")  # Indexwerte als numerische Werte

    # Sortieren der Daten nach Datum
    df = df.sort_values("Date").reset_index(drop=True)

    # Berechnung des SMA 200
    df["SMA_200"] = df["Value"].rolling(window=sma).mean()

    print("\nBacktesting Strategy:")

    # Backtesting Strategie
    capital = 10000  # Startkapital
    df = df[df["Date"] >= date].reset_index(drop=True)  # Backtest ab 2016
    position = capital / df.loc[0, "Value"]  # Sofortige Investition zum ersten verfügbaren Kurs
    capital = 0
    last_signal = "Buy"  # Starten mit einem Kauf

    for i in range(1, len(df)):
        current_price = df.loc[i, "Value"]
        sma_200 = df.loc[i, "SMA_200"]
        
        if pd.notna(sma_200):
            # Verkaufssignal: Preis ist 3% unter SMA 200
            if last_signal == "Buy" and current_price <= 1.00 * sma_200:
                capital = position * current_price  # Update capital based on the sold position
                position = 0
                last_signal = "Sell"
                print(f"{df.loc[i, 'Date'].date()} - SELL at {current_price:.2f}, Capital: {capital:.2f}")

            # Kaufsignal: Preis ist 2% über SMA 200
            elif last_signal == "Sell" and current_price > 1.00 * sma_200:
                position = capital / current_price  # Update position based on the capital
                capital = 0
                last_signal = "Buy"
                print(f"{df.loc[i, 'Date'].date()} - BUY at {current_price:.2f}, Position: {position:.2f}")
    
    # Endkapital berechnen
    final_value = capital + (position * df.loc[len(df) - 1, "Value"] if position > 0 else 0)
    return final_value
    

# Beispielaufruf
file_path = "703755 - MSCI World Momentum Index.csv.csv"  # Passe den Dateipfad an
date = '01.01.2015'
BuyAndHold = calculate_buy_and_hold(file_path, date)
final_capital = process_momentum_csv(file_path, date, 200)
print(f"Strategy: {final_capital:.2f}")
print(f"Buy and Hold: {BuyAndHold:.2f}")

