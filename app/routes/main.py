from flask import redirect, render_template, request, url_for, Blueprint,current_app, flash, jsonify, session, request
from app.forms import AddMealForm, AddMealTypeForm, SetGoalForm, AddNewProductForm, ShareForm
from flask_login import current_user, login_required
from app import db
from sqlalchemy import select, func, cast, Date, extract, func, cast, Date, extract, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import selectinload
from app.models import User
from app.models import FoodLog, FoodItem, MealType, User, ShareRecord
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Pie, Pie
import json, os, uuid
from app.forms import EditProfileForm, AddMealForm
from werkzeug.utils import secure_filename
import requests

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.get('/dashboard_home.html')
@login_required
def dashboard():
    try:
        recent_logs = db.session.scalars(
            select(FoodLog)
            .options(selectinload(FoodLog.food_details))
            .filter_by(user_id=current_user.id)
            .order_by(FoodLog.log_date.desc())
            .limit(5)
        ).all()
        print(f"Fetched recent logs for dashboard: {len(recent_logs)}")
    except Exception as e:
        print(f"Error fetching recent logs for dashboard: {e}")
        recent_logs = [] 

    edit_profile_form = EditProfileForm()
    edit_profile_form.first_name.data = current_user.first_name
    edit_profile_form.last_name.data = current_user.last_name    
      
    return render_template('dashboard_home.html',
                           title='Dashboard',
                           recent_logs=recent_logs,
                           user=current_user,
                           form=AddMealForm(),
                           edit_profile_form=edit_profile_form)

def get_week_of_year(dt):
    iso_calendar = dt.isocalendar()
    return iso_calendar[0], iso_calendar[1]

def get_year_month(dt):
    return dt.year, dt.month

@bp.route('/api/get_calorie_chart_options')
@login_required
def get_calorie_chart_options():
    time_range = request.args.get('range', 'week')
    share_id   = request.args.get('share_id', type=int)

    if share_id:
        share = ShareRecord.query.get_or_404(share_id)
        user_id = share.sender_id
        daily_calorie_goal = round(share.sender.target_calories or 0, 1)
    else:
        user_id = current_user.id
        daily_calorie_goal = round(current_user.target_calories or 0, 1)

    today = date.today()
    labels = []
    consumed_data = []

    query_start_date = None
    query_end_date = today

    if time_range == 'day':
        query_start_date = today
    elif time_range == 'week':
        query_start_date = today - timedelta(days=6)
    elif time_range == 'month':
        query_start_date = today.replace(day=1)
    else:
        return jsonify({"error": "Invalid time range parameter"}), 400

    try:
        calories_per_log = (
            func.coalesce(FoodLog.quantity_consumed, 0) / 100.0
        ) * func.coalesce(FoodItem.calories_per_100, 0)

        start_dt = datetime.combine(query_start_date, datetime.min.time())
        end_dt = datetime.combine(query_end_date, datetime.max.time())
        daily_calories_results = db.session.execute(
            select(
                func.strftime('%Y-%m-%d', FoodLog.log_date).label('log_day_str'),
                func.sum(calories_per_log).label('total_calories')
            )
            .select_from(FoodLog)
            .join(FoodItem, FoodLog.food_item_id == FoodItem.id)
            .where(
                FoodLog.user_id == user_id,
                FoodLog.log_date.between(start_dt, end_dt)
            )
            .group_by(func.strftime('%Y-%m-%d', FoodLog.log_date))
            .order_by(func.strftime('%Y-%m-%d', FoodLog.log_date))
        ).all()

        print(f"Executing calorie trend query for range '{time_range}' between {start_dt} and {end_dt}")
        print(f"Query Result (aggregated by day in DB): {daily_calories_results}")

        calories_by_day_str = {row.log_day_str: row.total_calories or 0 for row in daily_calories_results}
        print(f"Aggregated daily calories by date string: {calories_by_day_str}")

        if time_range == 'day':
            day_str = today.isoformat() # YYYY-MM-DD
            labels = [day_str]
            consumed_data = [round(calories_by_day_str.get(day_str, 0), 1)]

        elif time_range == 'week':
            start_date_for_labels = today - timedelta(days=6)
            for i in range(7):
                current_day = start_date_for_labels + timedelta(days=i)
                current_day_str = current_day.isoformat()
                labels.append(current_day.strftime('%m-%d'))
                consumed_data.append(round(calories_by_day_str.get(current_day_str, 0), 1))

        elif time_range == 'month':
            start_date_for_labels = today.replace(day=1)
            num_days_in_view = (today - start_date_for_labels).days + 1
            for i in range(num_days_in_view):
                current_day = start_date_for_labels + timedelta(days=i)
                current_day_str = current_day.isoformat()
                labels.append(current_day.strftime('%m-%d'))
                consumed_data.append(round(calories_by_day_str.get(current_day_str, 0), 1))

        print(f"Final labels for chart: {labels}")
        print(f"Final consumed_data for chart: {consumed_data}")

    except Exception as e:
        import traceback
        print(f"Error querying or processing calorie trend data: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "Could not retrieve or process calorie trend data"}), 500

    # daily_calorie_goal = round(current_user.target_calories or 0, 1)
    try:
        chart_title = f"Calorie Intake Trend ({time_range.capitalize()})"
        chart_object = None

        if time_range == 'day':
            if labels: chart_title = f"Calorie Intake ({labels[0]})"
            chart_object = Bar(init_opts=opts.InitOpts(width="100%", height="250px", bg_color="#FFFFFF"))
            chart_object.add_xaxis(xaxis_data=labels)
            chart_object.add_yaxis(
                series_name="Consumed", y_axis=consumed_data, # ...
            )
        else: # week or month
            chart_object = Line(init_opts=opts.InitOpts(width="100%", height="250px", bg_color="#FFFFFF"))
            chart_object.add_xaxis(xaxis_data=labels)
            chart_object.add_yaxis(
                series_name="Consumed", y_axis=consumed_data, is_smooth=True, # ...
            )
            chart_object.add_yaxis(
                series_name="Daily Goal", y_axis=[daily_calorie_goal] * len(labels), # ...
            )

        if chart_object is None:
             raise ValueError("Chart object was not created.")

        chart_object.set_global_opts(
             title_opts=opts.TitleOpts(title=chart_title, pos_left="center", title_textstyle_opts=opts.TextStyleOpts(font_size=14)),
             tooltip_opts=opts.TooltipOpts(trigger="axis" if time_range != 'day' else "item", axis_pointer_type="cross"),
             xaxis_opts=opts.AxisOpts(type_="category", name="Time"),
             yaxis_opts=opts.AxisOpts(type_="value",name="Calories (kcal)",axislabel_opts=opts.LabelOpts(formatter="{value}"),splitline_opts=opts.SplitLineOpts(is_show=True)),
             legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
             datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100) if time_range != 'day' else None, opts.DataZoomOpts(type_="inside", range_start=0, range_end=100) if time_range != 'day' else None,],
             toolbox_opts=opts.ToolboxOpts(is_show=True, feature=opts.ToolBoxFeatureOpts(save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(is_show=True)))
        )

        options_dict = json.loads(chart_object.dump_options())
        return jsonify(options_dict)

    except Exception as e:
        import traceback
        print(f"Error generating chart options with pyecharts: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Could not generate chart options"}), 500

@bp.route('/api/nutrition_ratio')
@login_required
def api_nutrition_ratio():
    target_date_str = request.args.get('date', date.today().isoformat())
    share_id   = request.args.get('share_id', type=int)

    if share_id:
        share = ShareRecord.query.get_or_404(share_id)
        user_id = share.sender_id
    else:
        user_id = current_user.id
    
    try:
        target_date = date.fromisoformat(target_date_str)
    except ValueError:
        target_date = date.today()

    try:
        protein_per_log = (func.coalesce(FoodLog.quantity_consumed, 0) / 100.0) * func.coalesce(FoodItem.protein_per_100, 0)
        fat_per_log = (func.coalesce(FoodLog.quantity_consumed, 0) / 100.0) * func.coalesce(FoodItem.fat_per_100, 0)
        carbs_per_log = (func.coalesce(FoodLog.quantity_consumed, 0) / 100.0) * func.coalesce(FoodItem.carbs_per_100, 0)

        date_str = target_date.isoformat()

        query = (
            select(
                func.sum(protein_per_log).label('total_protein'),
                func.sum(fat_per_log).label('total_fat'),
                func.sum(carbs_per_log).label('total_carbs')
            )
            .select_from(FoodLog) # 明确 select_from
            .join(FoodItem, FoodLog.food_item_id == FoodItem.id)
            .where(
                FoodLog.user_id == user_id,
                func.strftime('%Y-%m-%d', FoodLog.log_date) == date_str
            )
        )
        result = db.session.execute(query).first()

        protein_g = result.total_protein or 0
        fat_g = result.total_fat or 0
        carbs_g = result.total_carbs or 0

    except Exception as e:
        print(f"Error querying nutrition data for ratio: {e}")
        db.session.rollback()
        return jsonify({"error": "Could not retrieve nutrition data for ratio"}), 500

    protein_kcal = round(protein_g * 4, 1)
    fat_kcal = round(fat_g * 9, 1)
    carbs_kcal = round(carbs_g * 4, 1)
    total_kcal = protein_kcal + fat_kcal + carbs_kcal
    print("DEBUG nutrition grams:", protein_g, fat_g, carbs_g)

    pie_data = [
        ('Protein', protein_kcal),
        ('Fat', fat_kcal),
        ('Carbs', carbs_kcal)
    ]
    pie_data = [item for item in pie_data if item[1] > 0]

    try:
        pie_chart = (
            Pie(init_opts=opts.InitOpts(width="100%", height="250px", bg_color="#FFFFFF"))
            .add(
                series_name="Nutrient Calories",
                data_pair=pie_data,
                radius=["40%", "70%"],
                label_opts=opts.LabelOpts(is_show=False, position="center"),
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(orient="vertical", pos_left="left", pos_top="center"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="item", formatter="{a} <br/>{b}: {c} kcal ({d}%)"
                ),
            )
             .set_series_opts(
                 tooltip_opts=opts.TooltipOpts(
                    trigger="item", formatter="{a} <br/>{b}: {c} kcal ({d}%)"
                 ),
                 itemstyle_opts=opts.ItemStyleOpts(
                     border_color="#fff",
                     border_width=1,
                     border_radius=10
                 ),
                 label_opts=opts.LabelOpts(formatter="{b}: {d}%")
             )
        )

        options_dict = json.loads(pie_chart.dump_options())
        return jsonify(options_dict)

    except Exception as e:
        import traceback
        print(f"Error generating pie chart options with pyecharts: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Could not generate pie chart options"}), 500

@bp.route('/api/goal_leaderboard')
@login_required
def api_goal_leaderboard():
    period = request.args.get('period', '7d')
    share_id = request.args.get('share_id', type=int)

    today = date.today()
    if period == '30d':
        start_date = today - timedelta(days=29)
    else:
        start_date = today - timedelta(days=6)
    end_date = today

    if share_id:
        share     = ShareRecord.query.get_or_404(share_id)
        owner_id  = share.sender_id
    else:
        owner_id  = None

    LOWER_BOUND_FACTOR = 0.90
    UPPER_BOUND_FACTOR = 1.10

    try:
        calories_per_log = (
            func.coalesce(FoodLog.quantity_consumed, 0) / 100.0
        ) * func.coalesce(FoodItem.calories_per_100, 0)

        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        daily_calories_query = (
            select(
                FoodLog.user_id,
                func.strftime('%Y-%m-%d', FoodLog.log_date).label('log_day_str'),
                func.sum(calories_per_log).label('daily_calories')
            )
            .select_from(FoodLog)
            .join(FoodItem, FoodLog.food_item_id == FoodItem.id)
            .where(
                FoodLog.log_date.between(start_dt, end_dt),
                *( [FoodLog.user_id == owner_id] if owner_id else [] )
            )
            .group_by(FoodLog.user_id, func.strftime('%Y-%m-%d', FoodLog.log_date))
        )
        results = db.session.execute(daily_calories_query).all()

        user_ids_in_logs = {row.user_id for row in results}
        all_users_info = User.query.all()
        if not all_users_info:
            return jsonify([])

        user_data_map = {
            user.id: {
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'target': user.target_calories or 2000.0
            }
            for user in all_users_info
        }
        print(f"User data map fetched: {user_data_map}")

        achieved_days_count = defaultdict(int)
        daily_calories_per_user_day = defaultdict(lambda: defaultdict(float))
        for row in results:
            daily_calories_per_user_day[row.user_id][row.log_day_str] += row.daily_calories or 0

        current_check_date = start_date
        while current_check_date <= end_date:
            current_check_date_str = current_check_date.isoformat()
            for user_id, user_info in user_data_map.items():
                 daily_cals = daily_calories_per_user_day[user_id].get(current_check_date_str, 0)
                 target = user_info['target']
                 if target > 0:
                     lower_bound = target * LOWER_BOUND_FACTOR
                     upper_bound = target * UPPER_BOUND_FACTOR
                     if lower_bound <= daily_cals <= upper_bound:
                         achieved_days_count[user_id] += 1
            current_check_date += timedelta(days=1)

        print(f"Achieved days count: {dict(achieved_days_count)}")

        leaderboard = []
        for user_id, user_info in user_data_map.items():
            days_met = achieved_days_count.get(user_id, 0)
            first_name = user_info.get('first_name', '')
            last_name = user_info.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                full_name = f"User {user_id}"

            leaderboard.append({
                'user_id': user_id,
                'full_name': full_name,
                'first_name_for_sort': first_name.lower(),
                'last_name_for_sort': last_name.lower(),
                'days_met': days_met
            })

        leaderboard.sort(key=lambda x: (-x['days_met'], x['first_name_for_sort'], x['last_name_for_sort']))

        ranked_leaderboard = []
        rank = 0
        last_score = -1
        count_for_rank = 0
        for entry in leaderboard:
            count_for_rank += 1
            if entry['days_met'] != last_score:
                rank = count_for_rank
                last_score = entry['days_met']
            ranked_leaderboard.append({
                'user_id': entry['user_id'],       
                'rank': rank,
                'full_name': entry['full_name'],
                'days_met': entry['days_met']
            })

        print(f"Final leaderboard: {ranked_leaderboard}")
        return jsonify(ranked_leaderboard)

    except Exception as e:
        import traceback
        print(f"Error generating leaderboard: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "Could not generate leaderboard"}), 500

@bp.route('/api/ensure_food_item', methods=['POST'])
@login_required
def api_ensure_food_item():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing food name from API data'}), 400

    food_name_from_api = data.get('name')
    calories_100 = data.get('calories_per_100')
    protein_100 = data.get('protein_per_100')
    fat_100 = data.get('fat_per_100')
    carbs_100 = data.get('carbs_per_100')

    existing_food = db.session.scalar(
        select(FoodItem).where(FoodItem.name.ilike(food_name_from_api))
    )

    if existing_food:
        print(f"Food '{existing_food.name}' found in local DB with ID {existing_food.id}")
        return jsonify({
            'id': existing_food.id,
            'name': existing_food.name,
            'message': 'Food item already exists in local DB.'
        }), 200
    else:
        print(f"Food '{food_name_from_api}' not found in local DB. Attempting to add from API data.")
        if food_name_from_api and calories_100 is not None:
            try:
                new_food = FoodItem(
                    name=food_name_from_api,
                    calories_per_100 = float(calories_100),
                    protein_per_100  = float(protein_100) if protein_100 is not None else 0.0,
                    fat_per_100      = float(fat_100) if fat_100 is not None else 0.0,
                    carbs_per_100    = float(carbs_100) if carbs_100 is not None else 0.0,
                    serving_size=100.0,
                    serving_unit='g',
                    source='api_usda',
                    user_id=None
                )
                db.session.add(new_food)
                db.session.commit()
                print(f"New food '{new_food.name}' added to local DB with ID {new_food.id}")
                return jsonify({
                    'id': new_food.id,
                    'name': new_food.name,
                    'message': 'Food item added to local DB from API.'
                }), 201 # 201 Created
            except ValueError:
                db.session.rollback()
                print(f"ValueError adding food '{food_name_from_api}' from API: Invalid nutritional data format.")
                return jsonify({'error': 'Invalid nutritional data format from API. Could not add to local DB.'}), 400
            except Exception as e:
                db.session.rollback()
                print(f"Exception adding food '{food_name_from_api}' from API: {e}")
                return jsonify({'error': f'Failed to add food item to local DB: An internal error occurred.'}), 500
        else:
            print(f"Insufficient data from API for '{food_name_from_api}'. Not adding to local DB.")
            return jsonify({
                'error': 'Insufficient nutritional data from API to create new food item. Please add manually or try a different search.',
                'name_suggestion': food_name_from_api
            }), 400

def call_usda_api(name: str, max_results: int = 5) -> list[dict]:
    """
    调用 USDA API 返回最多 max_results 条数据
    每条数据包含 name, calories, protein, fat, carbs
    """
    api_key = os.getenv('USDA_API_KEY')
    if not api_key:
        raise RuntimeError("USDA_API_KEY is not set in environment")
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    params = {
        'query': name,
        'pageSize': max_results,
        'api_key': api_key
    }
    resp = requests.get(url, params=params, timeout=10)
    items = []
    if not resp.ok:
        return items

    data = resp.json().get('foods', [])
    for f in data:
        # 提取常用营养素
        nuts = {n['nutrientName']: n['value'] for n in f.get('foodNutrients', [])}
        items.append({
            'name':     f.get('description'),
            'calories': nuts.get('Energy'),
            'protein':  nuts.get('Protein'),
            'fat':       nuts.get('Total lipid (fat)'),
            'carbs':    nuts.get('Carbohydrate, by difference')
        })
    return items

@bp.route('/api/food/search', methods=['GET', 'POST'])
@login_required
def search_food():
    # GET 和 POST 都走同样逻辑，只是读取 name 的方式不同
    if request.method == 'POST':
        payload = request.get_json() or {}
        name = (payload.get('name') or '').strip()
    else:
        name = (request.args.get('name') or '').strip()

    if not name:
        return jsonify(results=[]), 200

    max_total = 10
    results = []

    # —— 构造 “自己或 admin 添加” 的过滤条件 —— 
    admin = User.query.filter_by(email='admin@dailybite.com').first()
    if hasattr(FoodItem, 'user_id'):
        user_cond = (FoodItem.user_id == current_user.id)
        suggestion_filter = or_(user_cond, FoodItem.user_id == admin.id) if admin else user_cond
    else:
        suggestion_filter = None

    # 1) 本地数据库匹配
    query = FoodItem.query
    if suggestion_filter is not None:
        query = query.filter(suggestion_filter)

    db_items = (
        query
        .filter(FoodItem.name.ilike(f'%{name}%'))
        .order_by(FoodItem.name)
        .limit(max_total)
        .all()
    )
    for it in db_items:
        results.append({
            'id':       it.id,
            'name':     it.name,
            'calories': it.calories_per_100,
            'protein':  it.protein_per_100,
            'fat':      it.fat_per_100,
            'carbs':    it.carbs_per_100,
            'quantity': it.serving_size if it.serving_size is not None else 100,
            'unit':     it.serving_unit or 'g'
        })

    # 2) 再调外部 API，补足到 max_total 条
    if len(results) < max_total:
        try:
            usda_list = call_usda_api(name, max_results=max_total - len(results))
        except Exception as e:
            current_app.logger.warning(f"USDA API error during search: {e}")
            usda_list = []
        seen = {r['name'] for r in results}
        for u in usda_list:
            if u['name'] not in seen:
                results.append(u)
                seen.add(u['name'])

    # 3) 如果两者都没数据，results 为空，前端会提示 “No results”
    return jsonify(results=results), 200


@bp.get('/addMeal')
@login_required
def addMeal():
    form = AddMealForm()
    edit_profile_form = EditProfileForm()
    if request.method == 'GET':
        edit_profile_form.first_name.data = current_user.first_name
        edit_profile_form.last_name.data = current_user.last_name
    user_meal_types_query = MealType.query.filter(MealType.user_id == current_user.id)
    system_default_meal_types_query = MealType.query.filter(MealType.user_id == None) 
    user_types = user_meal_types_query.order_by(MealType.type_name).all()
    system_types = system_default_meal_types_query.order_by(MealType.type_name).all()
    final_choices_dict = {} 
    preferred_order = ['Breakfast', 'Lunch', 'Dinner', 'Snacks']
    for type_name in preferred_order:
        found_system_type = next((st for st in system_types if st.type_name == type_name), None)
        if found_system_type:
            final_choices_dict[found_system_type.type_name] = found_system_type.type_name

    for st in system_types:
        if st.type_name not in final_choices_dict:
            final_choices_dict[st.type_name] = st.type_name
            
    for ut in user_types:
        if ut.type_name not in final_choices_dict:
            final_choices_dict[ut.type_name] = ut.type_name
            
    form.mealType.choices = list(final_choices_dict.items())

    if not form.mealType.choices:
        form.mealType.choices = [
            ('Breakfast', 'Breakfast'),
            ('Lunch', 'Lunch'),
            ('Dinner', 'Dinner'),
            ('Snacks', 'Snacks')
        ]

    print(f"Choices after form init and route processing: {form.mealType.choices}")

    historyItemsID = db.session.execute(select(FoodLog.food_item_id).where(FoodLog.user_id == current_user.id)).scalars().all()
    historyItemsNames = []
    if historyItemsID:
        historyItemsNames = db.session.execute(select(FoodItem.name).where(FoodItem.id.in_(historyItemsID))).scalars().all()

    admin = User.query.filter_by(email='admin@dailybite.com').first()
    suggestion_filter = None
    if hasattr(FoodItem, 'user_id'):
         suggestion_filter_user = (FoodItem.user_id == current_user.id)
         if admin:
             suggestion_filter = or_(suggestion_filter_user, FoodItem.user_id == admin.id)
         else:
             suggestion_filter = suggestion_filter_user

    if suggestion_filter is not None:
         suggestions_query_result = FoodItem.query.filter(suggestion_filter).order_by(FoodItem.id).all()
    else:
         suggestions_query_result = FoodItem.query.order_by(FoodItem.id).limit(20).all()

    suggestions_for_template = suggestions_query_result[:10]

    foodSearched = request.args.get("food")
    foodFound = []
    if foodSearched:
        foodFound = db.session.execute(
            select(FoodItem).where(FoodItem.name.ilike(f"%{foodSearched}%"))
        ).scalars().all()

    mealTypeParam = request.args.get('mealType')
    if mealTypeParam:
        form.mealType.data = mealTypeParam

    historyItemName = request.args.get('item')
    if historyItemName:
        historyItem = db.session.execute(
            select(FoodItem).where(FoodItem.name == historyItemName)
        ).scalars().one_or_none()
        if historyItem:
            form.food.data = historyItem.name
            form.quantity.data = historyItem.serving_size if historyItem.serving_size else 100
            form.unit.data = historyItem.serving_unit if historyItem.serving_unit else "g"
        else:
             form.unit.data = "g"
    else:
        form.unit.data = "g"

    print(f"Choices before render: {form.mealType.choices}")
    return render_template(
        'addMeal.html',
        form=form,
        foodFound=foodFound,
        historyItems=historyItemsNames,
        suggestions=suggestions_for_template,
        edit_profile_form=edit_profile_form
    )

@bp.post('/addMeal')
@login_required
def addMealPost():
    form = AddMealForm() 

    if form.validate_on_submit():
        foodName = form.food.data
        inputFood = db.session.scalar(select(FoodItem).where(FoodItem.name == foodName)) # 使用 scalar

        if not inputFood:
            flash("The food you chose is not yet in the database. Please add a new product in the settings", "error")
            return redirect(url_for('main.settings'))

        inputFoodID = inputFood.id
        try:
            foodLog = FoodLog(
                user_id=current_user.id,
                food_item_id=inputFoodID,
                meal_type=form.mealType.data,
                quantity_consumed=form.quantity.data,
                unit_consumed=form.unit.data
            )
            db.session.add(foodLog)
            db.session.commit()
            flash('Meal added successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving meal: {e}', 'danger')
            return redirect(url_for('main.addMeal'))
    else:
        print("--- Form validation FAILED in addMealPost ---")
        for field, errors in form.errors.items():
            for error in errors:
                field_label = field
                try:
                    field_label = getattr(form, field).label.text
                except AttributeError:
                    pass
                flash(f"Error in {field_label}: {error}", 'warning')
                print(f"Validation error in {field_label}: {error}")
        return redirect(url_for('main.addMeal'))

@bp.get('/settings')
@login_required
def settings():
    form1 = AddMealTypeForm()
    form2 = SetGoalForm()
    form3 = AddNewProductForm()
    edit_profile_form = EditProfileForm()
    
    admin = User.query.filter_by(email='admin@dailybite.com').first()

    meal_types = (
        MealType.query
                .filter(or_(
                    MealType.user_id == admin.id,             # Admin added
                    MealType.user_id == current_user.id   # user added
                ))
                .order_by(MealType.id.desc())
                .all()
    )
    
    return render_template('settings.html', form1=form1, form2=form2, form3=form3, meal_types=meal_types, edit_profile_form=edit_profile_form)

@bp.post('/addMealType')
@login_required
def addMealType():
    form1 = AddMealTypeForm()
    if form1.validate_on_submit(): 
        mealType = MealType(user_id=current_user.id, type_name=form1.typeName.data)
        db.session.add(mealType)
        db.session.commit()
        flash('Meal type added.', 'success')
    else:
        flash('Failed to add meal type.', 'danger')
    return redirect(url_for('main.settings', _anchor='mealType'))

@bp.delete('/meal-types/<int:mt_id>')
@login_required
def delete_meal_type(mt_id):
    mt = MealType.query.get_or_404(mt_id)
    if mt.user_id != current_user.id:
        abort(403)
    db.session.delete(mt)
    db.session.commit()
    return jsonify(success=True)

@bp.post('/setGoal')
@login_required
def setGoal():
    form2 = SetGoalForm()
    if form2.validate_on_submit(): 
        current_user.target_calories = form2.goal.data
        db.session.commit()
        flash('Goal set successfully.', 'success')
    else:
        flash('Failed to set your goal.', 'danger')
    return redirect(url_for('main.settings', _anchor='mealType'))

@bp.post('/addNewProduct')
@login_required
def addNewProduct():
    form = AddNewProductForm()
    if form.validate_on_submit():
        existing_food = db.session.scalar(
            select(FoodItem).where(FoodItem.name.ilike(form.name.data))
        )
        if existing_food:
            flash(f"Error: Food item '{form.name.data}' already exists!", "danger")
            return redirect(url_for('main.settings'))
        else:
            try:
                new_food = FoodItem(
                    name=form.name.data,
                    calories_per_100=form.calories_per_100.data, 
                    protein_per_100=form.protein_per_100.data,
                    fat_per_100=form.fat_per_100.data or 0.0,
                    carbs_per_100=form.carbs_per_100.data or 0.0,
                    serving_size=form.serving_size.data,
                    serving_unit=form.serving_unit.data,
                    category=form.category.data,
                    user_id=current_user.id
                )
                db.session.add(new_food)
                db.session.commit()
                flash(f"Food item '{new_food.name}' added successfully!", 'success')
                return redirect(url_for('main.settings'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving food item: {e}", 'danger')
                return redirect(url_for('main.settings'))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'warning')
        return redirect(url_for('main.settings'))

def time_ago(dt):
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"
    
@bp.route('/share', methods=['GET','POST'])
@login_required
def share():
    form = ShareForm()
    search_term = request.args.get('search','').strip()
    friends = []

    if search_term:
        friends = User.query \
            .filter(User.id != current_user.id) \
            .filter(or_(
                User.first_name.ilike(f"%{search_term}%"),
                User.last_name.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%")
            )).limit(10).all()

    if request.method == 'GET' and request.headers.get('Accept') == 'application/json':
        return jsonify([
            {'id': u.id,
             'first_name': u.first_name,
             'last_name': u.last_name,
             'email': u.email}
            for u in friends
        ])

    if request.method == 'POST':
        content_type = request.form.get('content_type')
        date_range   = request.form.get('date_range')
        selected_id  = request.form.get('selected_friend_id')

        if not selected_id:
            flash("Please select a friend to share with.", "warning")
            return redirect(request.referrer or url_for('main.dashboard'))

        new_share = ShareRecord(
            sender_id=current_user.id,
            receiver_id=int(selected_id),
            content_type=content_type,
            date_range=date_range,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(new_share)
        db.session.commit()
        flash("Content shared successfully.", "success")
        return redirect(url_for('main.dashboard'))

    return redirect(request.referrer or url_for('main.dashboard'))

@bp.route('/sharing_list')
def sharing_list():
    edit_profile_form = EditProfileForm()
    all_shares = ShareRecord.query \
        .filter_by(receiver_id=current_user.id) \
        .order_by(ShareRecord.timestamp.desc()) \
        .all()
    unread_count = sum(1 for s in all_shares if not s.is_read)
    for share in all_shares:
        share.elapsed_time = time_ago(share.timestamp)
    return render_template('sharing_list.html', shares=all_shares, unread_count=unread_count, edit_profile_form=edit_profile_form)

@bp.route('/share/<int:share_id>')
@login_required
def view_share(share_id):
    edit_profile_form = EditProfileForm()           

    share = ShareRecord.query.get_or_404(share_id)
    if share.receiver_id != current_user.id:
        abort(403)
    if not share.is_read:
        share.is_read = True
        db.session.commit()

    if share.date_range == 'day':
        period_label = "Today"
    elif share.date_range == 'week':
        period_label = "Last 7 days"
    elif share.date_range == 'month':
        period_label = "This month"
    else:
        period_label = "a custom period"

    return render_template('share_detail.html', share=share, period_label=period_label, edit_profile_form=edit_profile_form)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():

    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        f = form.avatar.data

        if f and allowed_file(f.filename):
            ext = f.filename.rsplit('.', 1)[1].lower()
            random_filename = str(uuid.uuid4()) + '.' + ext
            filename = secure_filename(random_filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            if current_user.avatar_filename:
                old_filepath = os.path.join(upload_folder, current_user.avatar_filename)
                if os.path.exists(old_filepath):
                    try:
                        os.remove(old_filepath)
                    except OSError as e:
                        print(f"Error removing old avatar {old_filepath}: {e}")
            try:
                f.save(filepath)
                current_user.avatar_filename = filename
            except Exception as e:
                 flash(f'Error saving avatar file: {e}', 'danger')
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')

        return redirect(url_for('main.dashboard'))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'warning')
        return redirect(url_for('main.dashboard'))
