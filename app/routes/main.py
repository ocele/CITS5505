from flask import redirect, render_template, request, url_for, Blueprint,current_app, flash
from app.forms import AddMealForm, AddMealTypeForm, SetGoalForm, AddNewProductForm
from flask_login import current_user, login_required
from app import db
from sqlalchemy import select, or_
from app.models import User
from app.models import FoodLog, FoodItem, MealType
from datetime import date

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # 打印 Flask 应用查找模板的路径列表
    print(f"DEBUG: Jinja Loader Searchpath: {current_app.jinja_loader.searchpath}")
    try:
        return render_template('index.html', title='Home')
    except Exception as e:
        print(f"ERROR rendering template: {e}")
        raise

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = AddMealForm()
    if form.validate_on_submit():
        foodName = form.food.data
        inputFoodItem = db.session.scalar(
            select(FoodItem).filter_by(name=foodNmae)
            ).one_or_none()

        if not inputFoodItem:
            flash(f"'{foodName}' Food not found, please add it", 'warning')
            return redirect(url_for('main.home'))
        else:
            try:
                foodLog = FoodLog(
                    user_id=current_user.id,
                    food_item_id=inputFoodItem.id,
                    meal_type=form.mealType.data,
                    quantity_consumed=float(form.quantity.data),
                )
                db.session.add(foodLog)
                db.session.commit()
                flash('Food loged!', 'success')
            except Exception as e:
                db.session.rollback() 
                flash(f'Adding error: {e}', 'danger')

            return redirect(url_for('main.home'))

    # form.mealType.choices = ["Breakfast", "Lunch", "Dinner", "Snacks"] 

    recent_logs = db.session.scalars(
        select(FoodLog).filter_by(user_id=current_user.id)
                      .order_by(FoodLog.log_date.desc())
                      .limit(5)
    ).all()


    return render_template(
        'profile.html', 
        title='My profile',
        user=user,
        form=form,
        recent_logs=recent_logs 
    )

    # return render_template('home_base.html', user=user)
    # return f"<h1>Welcome, {user.first_name} {user.last_name}!</h1>" 

@bp.get('/addMeal')
@login_required
def addMeal():
    form = AddMealForm()
    # 查询所有 MealType 选项
    admin = User.query.filter_by(email='admin@DailyBite.com').first()
    # 用户只能选自己或者admin加的类型，不能选别人的。
    mealtypes = MealType.query.filter(
        (MealType.user_id == current_user.id) | (MealType.user_id == admin.id)
    ).all()

      
    form.mealType.choices = [(m.id, m.type_name) for m in mealtypes]
    # DONE: customised choices of mealType

    historyItemsID = db.session.execute(select(FoodLog.food_item_id).where(FoodLog.user_id == current_user.id)).scalars().all()
    historyItemsNames = []
    if historyItemsID:
        historyItemsNames = db.session.execute(select(FoodItem.name).where(FoodItem.id.in_(historyItemsID))).scalars().all()
    
    suggestions = FoodItem.query.filter(
        or_(
            FoodItem.user_id == current_user.id,
            FoodItem.user_id == admin.id
        )
    ).order_by(FoodItem.id).all()# 按id升序排序

    if not suggestions:
        suggestionsTopTen = []
    elif len(suggestions) > 10:
        suggestionsTopTen = suggestions[:10]
    else:
        suggestionsTopTen = suggestions
    # I picked only ten suggestions to avoid the list being too long
    # DONE: Some sort of priority might come handy here. V: sort by id.

    foodFound = request.args.getlist('foodFound')
    form.mealType.data= request.args.get('mealType')
    historyItem = request.args.get('item')
    if historyItem:
        form.food = historyItem.name
        form.quantity = historyItem.serving_size
        form.unit = historyItem.serving_unit
    
    return render_template('addMeal.html', form=form, foodFound=foodFound, historyItems=historyItemsNames, suggestions=suggestionsTopTen)

@bp.post('/addMeal')
@login_required
def addMealPost():
    form = AddMealForm()
    if form.validate_on_submit():
        foodName = form.food.data
        inputFood = db.session.execute(select(FoodItem).where(FoodItem.name == foodName).one_or_none())
        if not inputFood:
            # foodItem = FoodItem(name = foodName, serving_size = form.quantity.data, serving_unit = form.unit.data, calories = 0 ) 
            # # TODO: What are the calories for a new item???
            # db.session.add(foodItem)
            # db.session.commit()
            flash("The food you chose is not yet in the database. Please add a new product in the setting", "error")
            return redirect(url_for('index.html')) # TODO: change the url to settings
            
        # Create and add new food log entry
        inputFoodID = db.session.execute(select(FoodItem.id).where(FoodItem.name == foodName).scalars.one_or_none())
        foodLog = FoodLog(user_id = current_user.id, food_item_id = inputFoodID, meal_type = form.mealType.data, quantity_consumed = form.quantity.data, unit_consumed = form.unit.data)
        db.session.add(foodLog)
        db.session.commit() 
        return redirect(url_for('index.html')) # TODO: add home page url here
    else:
        return redirect(url_for('addMeal'))

@bp.route('/searchFood')
@login_required
def searchFood():
    form = AddMealForm()
    mealType = form.mealType.data
    foodSearched = form.food.data
    foodFound = db.session.execute(select(FoodItem.name, FoodItem.calories, FoodItem.serving_size, FoodItem.serving_unit).where(FoodItem.name.ilike(f"%{foodSearched}%"))).all()
    return redirect(url_for('main.addMeal', foodFound = foodFound, mealType = mealType))

@bp.route('/getHistory')
@login_required
def getHistory():
    form = AddMealForm()
    mealType = form.mealType.data
    item = request.args.get('item')
    history = db.session.execute(select(FoodItem).where(FoodItem.name == item))

    return redirect(url_for('addMeal', mealType = mealType, item = history))

@bp.get('/setting')
@login_required
def setting():
    form1 = AddMealTypeForm()
    form2 = SetGoalForm()
    form3 = AddNewProductForm()
    
    return render_template('setting.html', form1=form1, form2=form2, form3=form3)

@bp.post('/addMealType')
@login_required
def addMealType():
    form1 = AddMealTypeForm()
    if form1.validate_on_submit(): 
        mealType = MealType(user_id=current_user.id, type_name=form1.typeName.data)
        db.session.add(mealType)
        db.session.commit()
        return redirect(url_for()) # TODO: homepage
    else:
        return redirect(url_for('setting'))

@bp.post('/setGoal')
@login_required
def setGoal():
    form2 = SetGoalForm()
    if form2.validate_on_submit(): 
        current_user.target_calories = form2.goal.data
        db.session.commit()
        return redirect(url_for()) # TODO: homepage
    else:
        return redirect(url_for('setting'))

@bp.post('/addNewProduct')
@login_required
def addNewProduct():
    form3 = AddNewProductForm()
    if form3.validate_on_submit():
        if db.session.execute(select(FoodItem).where(FoodItem.name == form3.productName.data).one_or_none):
            flash("Error: The food with the same name already exist!", "error")
            return redirect(url_for('setting'))
        else:
            foodItem = FoodItem(name=form3.productName.data, serving_size=form3.quantity.data, serving_unit=form3.unit.data, calories=form3.kilojoules.data)
            db.session.add(foodItem)
            db.session.commit()
            return redirect(url_for()) # TODO: homepage
    else:
        return redirect(url_for('setting'))
    
@bp.route('/friends')
@login_required
def friends():

    return "friends page" # TODO: need a friends page

@bp.route('/meal_list')
def meal_list():

    # TODO: need a meal list page
    return "Meal List page coming soon!"

@bp.route('/settings')
def settings():

    # TODO: need a settings page
    return "settings page coming soon!"


# def index():
#     print(f"DEBUG: App template folder: {current_app.template_folder}") # 打印模板文件夹路径
#     try:
#         return render_template('index.html', title='Home')
#     except Exception as e:
#         print(f"ERROR rendering template: {e}") # 打印渲染时的具体错误
#         raise #
#     # user = {'username': current_user.username} # 示例
#     # return render_template('index.html', title='Home', user=user)
#     return render_template('index.html', title='Home') # 先渲染一个简单的首页

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     form1 = LoginForm()
#     form2 = RegisterForm()
#     if request.method == "POST":
#         if not form1.validate_on_submit() and not form2.validate_on_submit():
#             errorMessage = "Please fill all necessary field!"
#         else:
#             formType = request.form.get('form_type')
#             if formType == 'login':
#                 email = form1.emailLogin.data
#                 password = form1.passwordLogin.data

#                 #  TODO:Account Verification 

#                 return redirect () # TODO:Redirect to the user page
            
#             elif formType == 'register':
#                 email = form2.emailRegister.data
#                 password = form2.passwordRegister.data
#                 firstName = form2.firstName.data
#                 lastName = form2.lastName.data
#                 subscription = form2.subscription.data # Do we really need to send emails tho?

#                 # TODO:Account registration

#                 return redirect () # TODO:Redirect to the user page
#                 '''I don't know if it is appropriate to automatically redirect directly
#                 to the user page right after the registration. I mean, many websites still
#                 require you to sign in even when you just finished register an accnount.
#                 Personnaly, I take that as a nuisance. But I guess there might be some reason 
#                 behind that kind of design. If so, please let me know and I'll change the code.'''
        
#     return render_template('login.html', form1 = form1, form2 = form2, errorMessage = errorMessage)