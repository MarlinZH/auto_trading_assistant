# YOUR Investments DB schema mapping
INVESTMENTS_PROPERTIES = {
    "Name": {"title": [{"text": {"content": symbol}}]},
    "Ticker Symbol": {"rich_text": [{"text": {"content": ticker}}]},
    "Quantity": {"number": quantity},  # 5 decimal precision
    "Average Price": {"number": avg_price},
    "Equity": {"number": equity},
    "Investment Strategy": {"select": {"name": strategy}},  # Sell/Hold/Buy/Collect/Review/Reposition
    "Position": {"select": {"name": position}},  # UP/DOWN
    "Industry": {"rich_text": [{"text": {"content": industry}}]}
}

# YOUR Options Watch DB schema mapping
OPTIONS_PROPERTIES = {
    "Name": {"title": [{"text": {"content": option_name}}]},
    "Status": {"select": {"name": status}},  # Active/Historic/Watching/Utilized
    "Cost @ Add": {"number": cost_at_add},
    "Peak": {"number": peak_price},
    "Purchase Price": {"number": purchase_price},
    "Sell Price": {"number": sell_price},
    "Outcome": {"rich_text": [{"text": {"content": outcome}}]}
    # Unrealized Profit is a formula - auto-calculated
}
