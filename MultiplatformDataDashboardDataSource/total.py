import json
from pathlib import Path

file_path = Path(__file__).parent / 'Tiktok' / 'ProfitAnalysis.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

total_profit = sum(item.get('total_profit', 0) for item in data)
print(f"总毛利: {round(total_profit, 2)}") 