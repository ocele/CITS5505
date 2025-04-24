from flask import redirect, render_template, request, url_for, Blueprint,current_app
from app.forms import LoginForm, RegisterForm
from flask_login import current_user

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

@bp.route('/addMeal')
def addMeal():
    # TODO:
    return

@bp.route('/getHistory')
def getHistory():
    # TODO:
    item = request.args.get('item')
    return
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