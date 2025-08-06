from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ApplianceForm(FlaskForm):
    name = StringField('Appliance Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Kitchen', '🍳 Kitchen'),
        ('Entertainment', '📺 Entertainment'),
        ('Climate Control', '❄️ Climate Control'),
        ('Lighting', '💡 Lighting'),
        ('Laundry', '👕 Laundry'),
        ('Computing', '💻 Computing'),
        ('Other', '📦 Other')
    ], validators=[DataRequired()])  # 修改为 SelectField，并添加 choices
    wattage = IntegerField('Power (Watts)', validators=[DataRequired()])  # 设置为必填
    submit = SubmitField('Add Appliance')

