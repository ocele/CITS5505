from flask import redirect, render_template, request, url_for, Blueprint,current_app
from app.forms import AddMealForm
from flask_login import current_user, login_required
from app import db
from sqlalchemy import select
from app.models import FoodLog, FoodItem

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

@bp.get('/addMeal')
@login_required
def addMeal():
    form = AddMealForm()
    form.mealType.choices = ["breakfast", "lunch", "supper", "dinner", "snacks"]
    # TODO: customised choices of mealType

    historyItemsID = db.session.execute(select(FoodLog.food_item_id).where(FoodLog.user_id == current_user.id)).scalars().all()
    historyItemsNames = []
    if historyItemsID:
        historyItemsNames = db.session.execute(select(FoodItem.name).where(FoodItem.id.in_(historyItemsID))).scalars().all()

    suggestions = db.session.execute(select(FoodItem.name, FoodItem.calories, FoodItem.serving_size, FoodItem.serving_unit)).all()
    if not suggestions:
        suggestions = []
    elif len(suggestions) > 10:
        suggestionsTopTen = suggestions[:10]
    else:
        suggestionsTopTen = suggestions
    # I picked only ten suggestions to avoid the list being too long
    # TODO: Some sort of priority might come handy here

    foodFound = request.args.getlist('foodFound', default=[])
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
        if not inputFood: # Create a new food item entry if the input food is not recorded yet in the database
            foodItem = FoodItem(name = foodName, serving_size = form.quantity.data, serving_unit = form.unit.data, calories = 0 ) 
            # TODO: What are the calories for a new item???
            db.session.add(foodItem)
            db.session.commit()
        
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
    foodFound = db.session.execute(select(FoodItem.name, FoodItem.calories, FoodItem.serving_size, FoodItem.serving_unit).where(FoodItem.name == foodSearched).all())
    return redirect(url_for('addMeal', foodFound = foodFound, mealType = mealType))

@bp.route('/getHistory')
@login_required
def getHistory():
    form = AddMealForm()
    mealType = form.mealType.data
    item = request.args.get('item')
    history = db.session.execute(select(FoodItem).where(FoodItem.name == item))

    return redirect(url_for('addMeal', mealType = mealType, item = history))


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