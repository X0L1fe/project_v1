from flask import Flask, render_template, url_for, request, redirect

import app

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import email_validator

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class RegisterForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    repeat_password = PasswordField('Повторите пароль:', validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')



@app.route('/registering', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        login = form.login.data
        email = form.email.data
        password = form.password.data
        repeat_password = form.repeat_password.data
        remember_me = form.remember_me.data
        submit = form.submit.data
        if password == repeat_password and login != "" and password != "" and repeat_password != "":
            print(login, email, password, repeat_password,  remember_me, submit)
            return {"login": login,
                "email": email,
                "password": password,
                "repeat_password": repeat_password,
                "remeber": remember_me,
                "submit": submit
                }
        else:
            return redirect('/registering')
    return render_template('reg.html', form=form)


@app.route('/logining', methods=['GET', 'POST'])
def logIN():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        remember_me = form.remember_me.data
        submit = form.submit.data
        if login != "" and password != "":
            print(login, password, remember_me, submit)
            return {"login": login,
                    "password": password,
                    "remeber": remember_me,
                    "submit": submit
                    }
    return render_template('log.html', form=form)