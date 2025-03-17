from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os

daily_goods_bp = Blueprint('daily_goods', __name__)

current_dir = os.path.dirname(__file__)  # 当前文件所在目录
DAILY_GOODS_DIR = os.path.join(current_dir, 'data')
DAILY_GOODS_FILE = os.path.join(DAILY_GOODS_DIR, 'daily_goods.txt')

def load_daily_goods():
    daily_goods = []
    if os.path.exists(DAILY_GOODS_FILE):
        with open(DAILY_GOODS_FILE, 'r', encoding='utf-8') as file:
            daily_goods = json.load(file)
    current_date = datetime.now()
    for good in daily_goods:
        input_date_str = good['input_date']
        input_date = datetime.fromisoformat(input_date_str)
        expected_days = good.get('expected_days', None)
        if expected_days is not None:
            days_used = (current_date - input_date).days
            remaining_days = expected_days - days_used
            good['remaining_days'] = remaining_days
        else:
            good['remaining_days'] = None
    return daily_goods

def save_daily_goods(daily_goods):
    os.makedirs(DAILY_GOODS_DIR, exist_ok=True)
    with open(DAILY_GOODS_FILE, 'w', encoding='utf-8') as file:
        json.dump(daily_goods, file, ensure_ascii=False, indent=4)

# 显示日用品列表
@daily_goods_bp.route('/daily_goods')
def daily_goods():
    daily_goods = load_daily_goods()
    return render_template('daily_goods.html', daily_goods=daily_goods)

# 添加日用品处理（表单提交）
@daily_goods_bp.route('/add_daily_good', methods=['POST'])
def add_daily_good():
    daily_goods = load_daily_goods()
    new_good = {
        'name': request.form['name'],
        'purchase_date': request.form['purchase_date'],
        'purchase_price': float(request.form['purchase_price']),
        'quantity': int(request.form['quantity']),
        'unit': request.form['unit'],
        'expected_days': int(request.form['expected_days']) if request.form['expected_days'] else None,
        'storage_location': request.form['storage_location'],
        'input_date': datetime.now().isoformat()
    }
    daily_goods.append(new_good)
    save_daily_goods(daily_goods)
    return redirect(url_for('daily_goods.daily_goods'))
@daily_goods_bp.route('/decrease_quantity/<good_name>', methods=['POST'])
def decrease_quantity(good_name):
    daily_goods = load_daily_goods()
    for good in daily_goods:
        if good['name'] == good_name and good['quantity'] > 0:
            good['quantity'] -= 1  # 数量减一
            break
    save_daily_goods(daily_goods)
    return redirect(url_for('daily_goods.daily_goods'))
# 管理日用品页面
@daily_goods_bp.route('/manage_daily_goods')
def manage_daily_goods_page():
    daily_goods = load_daily_goods()
    return render_template('manage_daily_goods.html', daily_goods=daily_goods)

# 删除日用品
@daily_goods_bp.route('/delete_daily_good/<good_name>', methods=['POST'])
def delete_daily_good(good_name):
    daily_goods = load_daily_goods()
    updated_goods = [good for good in daily_goods if good['name'] != good_name]
    save_daily_goods(updated_goods)
    return redirect(url_for('daily_goods.manage_daily_goods_page'))

# 新增：编辑日用品页面
@daily_goods_bp.route('/edit_daily_good/<good_name>')
def edit_daily_good_page(good_name):
    daily_goods = load_daily_goods()
    target_good = next((good for good in daily_goods if good['name'] == good_name), None)
    return render_template('edit_daily_good.html', good=target_good)

# 新增：处理编辑日用品提交
@daily_goods_bp.route('/edit_daily_good/<good_name>', methods=['POST'])
def edit_daily_good(good_name):
    daily_goods = load_daily_goods()
    target_index = next((i for i, good in enumerate(daily_goods) if good['name'] == good_name), -1)
    if target_index != -1:
        updated_good = {
            'name': request.form['name'],
            'purchase_date': request.form['purchase_date'],
            'purchase_price': float(request.form['purchase_price']),
            'quantity': int(request.form['quantity']),
            'unit': request.form['unit'],
            'expected_days': int(request.form['expected_days']) if request.form['expected_days'] else None,
            'storage_location': request.form['storage_location'],
            'input_date': daily_goods[target_index]['input_date']  # 保留原始录入时间
        }
        daily_goods[target_index] = updated_good
        save_daily_goods(daily_goods)
    return redirect(url_for('daily_goods.manage_daily_goods_page'))