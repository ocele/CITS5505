from flask import redirect, render_template, request, url_for, Blueprint,current_app, flash
from app.forms import AddMealForm, AddMealTypeForm, SetGoalForm, AddNewProductForm
from flask_login import current_user, login_required
from app import db
from sqlalchemy import select
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

@bp.get('/dashboard_home.html')
@login_required
def dashboard():
    return render_template('dashboard_home.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = AddMealForm()
    if form.validate_on_submit():
        foodName = form.food.data
        inputFoodItem = db.session.scalar(
            select(FoodItem).filter_by(name=foodName)
            ).one_or_none()

        if not inputFoodItem:
            flash(f"'{foodName}' Food not found, please add it", 'warning')
            return redirect(url_for('main.dashboard'))
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

            return redirect(url_for('main.dashboard'))

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
    # defaultChoices = ["breakfast", "lunch", "supper", "dinner", "snacks"]
    # userMealtype = [ meal.type_name for meal in current_user.meal_types.all()]
    # form.mealType.choices = defaultChoices + userMealtype

    historyItemsID = db.session.execute(select(FoodLog.food_item_id).where(FoodLog.user_id == current_user.id)).scalars().all()
    historyItemsNames = []
    if historyItemsID:
        historyItemsNames = db.session.execute(select(FoodItem.name).where(FoodItem.id.in_(historyItemsID))).scalars().all()
        historyItemsNames = historyItemsNames[:8] # Limit the showing items to 8 items

    suggestions = db.session.execute(select(FoodItem.name, FoodItem.calories, FoodItem.serving_size, FoodItem.serving_unit)).all()
    if not suggestions:
        suggestionsTopTen = []
    elif len(suggestions) > 10:
        suggestionsTopTen = suggestions[:10]
    else:
        suggestionsTopTen = suggestions
    # I picked only ten suggestions to avoid the list being too long
    # TODO: Some sort of priority might come handy here

    foodSearched = request.args.get("food")
    if foodSearched:
        foodFound = db.session.execute(select(FoodItem).where(FoodItem.name.ilike(f"%{foodSearched}%"))).scalars().all()
    else:
        foodFound = []
        
    form.mealType.data= request.args.get('mealType')

    historyItemName = request.args.get('item')
    if historyItemName:
        historyItem = db.session.execute(select(FoodItem).where(FoodItem.name == historyItemName)).scalars().one()
        form.food.data = historyItem.name
        form.quantity.data = historyItem.serving_size
        form.unit.data = historyItem.serving_unit
    else:
        form.unit.data = "gram"
    
    return render_template('addMeal.html', form=form, foodFound=foodFound, historyItems=historyItemsNames, suggestions=suggestionsTopTen)

@bp.post('/addMeal')
@login_required
def addMealPost():
    form = AddMealForm()
    if form.validate_on_submit():
        foodName = form.food.data
        inputFood = db.session.execute(select(FoodItem).where(FoodItem.name == foodName)).scalars().one_or_none()
        if not inputFood:
            # foodItem = FoodItem(name = foodName, serving_size = form.quantity.data, serving_unit = form.unit.data, calories = 0 ) 
            # db.session.add(foodItem)
            # db.session.commit()
            flash("The food you chose is not yet in the database. Please add a new product in the settings", "error")
            return redirect(url_for('main.settings')) 
            
        # Create and add new food log entry
        inputFoodID = inputFood.id
        foodLog = FoodLog(user_id = current_user.id, food_item_id = inputFoodID, meal_type = form.mealType.data, quantity_consumed = form.quantity.data, unit_consumed = form.unit.data)
        db.session.add(foodLog)
        db.session.commit() 
        return redirect(url_for('main.dashboard'))
    else:
        flash("The form validation failed", "error")
        return redirect(url_for('main.addMeal'))

# @bp.route('/searchFood')
# @login_required
# def searchFood():
#     form = AddMealForm()
#     mealType = request.args.get("mealType")
#     foodSearched = request.args.get("food")
#     print ("retrieved data is", form.food.data)
#     foodFound = db.session.execute(select(FoodItem).where(FoodItem.name.ilike(f"%{foodSearched}%"))).all()
#     print("This is the food found", foodFound, type(foodFound))
#     return redirect(url_for('main.addMeal', foodFound = foodFound, mealType = mealType))

# @bp.route('/getHistory')
# @login_required
# def getHistory():
#     form = AddMealForm()
#     mealType = form.mealType.data
#     item = request.args.get('item')
#     history = db.session.execute(select(FoodItem).where(FoodItem.name == item)).scalars()

#     return redirect(url_for('main.addMeal', mealType = mealType, item = history))

@bp.get('/settings')
@login_required
def settings():
    form1 = AddMealTypeForm()
    form2 = SetGoalForm()
    form3 = AddNewProductForm()
    
    return render_template('settings.html', form1=form1, form2=form2, form3=form3)

@bp.post('/addMealType')
@login_required
def addMealType():
    form1 = AddMealTypeForm()
    if form1.validate_on_submit(): 
        mealType = MealType(user_id=current_user.id, type_name=form1.typeName.data)
        db.session.add(mealType)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.settings'))

@bp.post('/setGoal')
@login_required
def setGoal():
    form2 = SetGoalForm()
    if form2.validate_on_submit(): 
        current_user.target_calories = form2.goal.data
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.settings'))

@bp.post('/addNewProduct')
@login_required
def addNewProduct():
    form3 = AddNewProductForm()
    if form3.validate_on_submit():
        if db.session.execute(select(FoodItem).where(FoodItem.name == form3.productName.data)).one_or_none():
            flash("Error: The food with the same name already exist!", "error")
            return redirect(url_for('main.settings'))
        else:
            foodItem = FoodItem(name=form3.productName.data, serving_size=form3.quantity.data, serving_unit=form3.unit.data, calories=form3.kilojoules.data)
            db.session.add(foodItem)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.settings'))
    
@bp.route('/friends')
@login_required
def share():

    return render_template('share.html')

@bp.route('/sharin_list')
def sharing_list():
    return render_template('sharing_list.html')




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