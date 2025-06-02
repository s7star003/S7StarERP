import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'MultiplatformDataDashboardDataSource')
OUTPUT_DIR = os.path.join(DATA_DIR, 'MultiplatformMerger')
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'MultiplatformDataMerged.json')

platforms = ['Shein', 'Miravia', 'Amazon', 'TikTok']
# 统一的分析类型（文件名去掉.json）
analysis_types = set()
platform_files = {}
for platform in platforms:
    platform_path = os.path.join(DATA_DIR, platform)
    if not os.path.exists(platform_path):
        continue
    files = [f for f in os.listdir(platform_path) if f.endswith('.json')]
    platform_files[platform] = files
    for f in files:
        analysis_types.add(f.replace('.json', ''))

# 合并数据结构：{平台: {分析类型: 数据}}
merged = {}
for platform in platforms:
    merged[platform] = {"platform": platform}
    platform_path = os.path.join(DATA_DIR, platform)
    for analysis in analysis_types:
        file_path = os.path.join(platform_path, analysis + '.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    merged[platform][analysis] = json.load(f)
            except Exception as e:
                merged[platform][analysis] = f"读取失败: {e}"
        else:
            merged[platform][analysis] = None

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

# 新增：生成所有平台的总比较
all_platform = {}
for analysis in analysis_types:
    all_platform[analysis] = []
    for platform in platforms:
        data = merged[platform].get(analysis)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item = dict(item)  # 拷贝，避免污染原数据
                    item['platform'] = platform
                all_platform[analysis].append(item)
    # BuyerAnalysis按total_amount倒序
    if analysis == 'BuyerAnalysis':
        all_platform[analysis].sort(key=lambda x: x.get('total_amount', 0), reverse=True)
    # ReturnRate按return_rate倒序
    elif analysis == 'ReturnRate':
        all_platform[analysis].sort(key=lambda x: x.get('return_rate', 0), reverse=True)
    # AreaDemand_all按sales_amount倒序
    elif analysis == 'AreaDemand_all':
        all_platform[analysis].sort(key=lambda x: x.get('sales_amount', 0), reverse=True)
    # OrderAnalysis按sell_count倒序
    elif analysis == 'OrderAnalysis':
        all_platform[analysis].sort(key=lambda x: x.get('sell_count', 0), reverse=True)
    # ProfitAnalysis按total_profit倒序
    elif analysis == 'ProfitAnalysis':
        all_platform[analysis].sort(key=lambda x: x.get('total_profit', 0), reverse=True)
    # SalesRank_all按sales倒序
    elif analysis == 'SalesRank_all':
        all_platform[analysis].sort(key=lambda x: x.get('sales', 0), reverse=True)
    # MonthlySalesAnalysis按total_amount、sales倒序
    elif analysis == 'MonthlySalesAnalysis':
        all_platform[analysis].sort(key=lambda x: (x.get('total_amount', 0), x.get('sales', 0)), reverse=True)
    # 其它分析类型优先按sales_amount倒序排，没有则按sales倒序排
    else:
        all_platform[analysis].sort(key=lambda x: (x.get('sales_amount', 0), x.get('sales', 0)), reverse=True)

# 合并到总数据结构
merged['AllPlatform'] = all_platform

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"多平台分析数据已合并输出到: {OUTPUT_FILE}") 