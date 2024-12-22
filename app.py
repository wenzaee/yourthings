from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
def load_assets():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
# File to store asset data
DATA_FILE = 'data/assets.txt'
data = {
    "assets": load_assets()
}
# Load assets from the file


# Save assets to the file
def save_assets(assets):
    with open(DATA_FILE, 'w') as file:
        json.dump(assets, file)



# 保存资产到文件
def save_assets(assets):
    with open(DATA_FILE, 'w') as file:
        json.dump(assets, file, ensure_ascii=False, indent=4)

@app.route('/delete_asset/<asset_name>', methods=['DELETE'])
def delete_asset(asset_name):
    #assets = load_assets()  # 从文件加载资产
    data["assets"] = load_assets()
    # 找到并删除匹配名称的资产
    updated_assets = [asset for asset in data["assets"] if asset['name'] != asset_name]
    
    # 如果删除成功，更新文件
    if len(updated_assets) < len(data["assets"]):
        save_assets(updated_assets)
        return redirect(url_for('dashboard'))  # 删除成功后重定向到资产总览页面
    else:
        return jsonify({"success": False, "message": f"Asset '{asset_name}' not found."})


@app.route('/')
def dashboard():
    # 加载最新的资产数据
    #data = {
     #   "assets": load_assets()  # 每次访问都重新加载资产数据
    #}
    data["assets"] = load_assets()
    # 计算总资产
    total_value = sum(asset['value'] for asset in data['assets'])
    
    # 计算每个资产的日均资产和购买天数
    for asset in data['assets']:
        asset['daily_average'] = calculate_asset_daily_average(asset)
        asset['purchase_days'] = calculate_purchase_days(asset)

    # 计算总日均资产
    total_daily_average = calculate_total_daily_average()

    # 渲染页面并传递数据
    return render_template('dashboard.html', assets=data['assets'], total_daily_average=total_daily_average, total_value=total_value)


@app.route('/add_asset_page')
def add_asset_page():
    data["assets"] = load_assets()  # 从文件加载资产
    return render_template('add_asset.html', assets=data["assets"])


@app.route('/add_asset', methods=['POST'])
def add_asset():
    asset = request.json
    asset["value"] = float(asset["value"])
    asset["purchase_date"] = datetime.strptime(asset["purchase_date"], '%Y-%m-%d').isoformat()
    asset["icon"] = asset.get("icon", "default.png")  # 默认图标
    data['assets'].append(asset)
    save_assets(data['assets'])
    return jsonify({"message": "Asset added successfully!", "assets": data['assets']})

@app.route('/clear_assets', methods=['POST'])
def clear_assets():
    data['assets'] = []
    save_assets(data['assets'])
    return jsonify({"message": "All assets cleared!", "assets": data['assets']})

def calculate_asset_daily_average(asset):
    today = datetime.now()
    purchase_date = datetime.fromisoformat(asset['purchase_date'])
    days_held = max((today - purchase_date).days, 1)  # At least 1 day to avoid division by zero
    return round(asset['value'] / days_held, 2)

def calculate_purchase_days(asset):
    today = datetime.now()
    purchase_date = datetime.fromisoformat(asset['purchase_date'])
    days_held = max((today - purchase_date).days, 1)  # At least 1 day to avoid division by zero
    return days_held

def calculate_total_daily_average():
    if not data['assets']:
        return 0
    total_average = sum(calculate_asset_daily_average(asset) for asset in data['assets'])
    return round(total_average, 2)

if __name__ == '__main__':
    app.run(debug=False)
