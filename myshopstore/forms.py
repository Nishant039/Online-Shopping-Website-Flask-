from flask_wtf import FlaskForm

from wtforms import StringField,PasswordField,SubmitField,ValidationError,TextAreaField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo

from myshopstore.models import User,Item,Info

from flask_wtf.file import FileField,FileAllowed 

import re
class RegistrationForm(FlaskForm):

	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])

	email=StringField('Email',validators=[Email(),DataRequired()])

	password=PasswordField('Password',validators=[DataRequired()])

	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])


	submit=SubmitField('Register')
	def validate_username(self,username):

		user=User.query.filter_by(username=username.data).first()

		if user:
			raise ValidationError("Username Already Taken")

	def validate_email(self,email):
		user=User.query.filter_by(email=email.data).first()

		if user:
			raise ValidationError("Email Already Registered")


class LoginForm(FlaskForm):
	email=StringField('Email',validators=[Email(),DataRequired()])

	password=PasswordField('Password',validators=[DataRequired()])

	submit=SubmitField('Login')


class ItemForm(FlaskForm):
	name=StringField("Name",validators=[DataRequired()])

	image=FileField("Image of the Item",validators=[FileAllowed(['jpg','jpeg','png'])])

	gender=StringField("Gender Of the Item (M/F)",validators=[DataRequired(),Length(min=1,max=1)])

	size=StringField("Size of the Item if applicable",validators=[Length(min=1,max=5)])

	cost=IntegerField("Enter the Cost of the Item")

	quantity=IntegerField("Available quantity Of the item ")

	submit=SubmitField("Upload")


	def validate_gender(self,gender):
		a=["M","F"]
		if gender.data not in a:
			print(gender)
			raise ValidationError("Please enter M for Male and F for Female")



class AddressForm(FlaskForm):

	address=TextAreaField("Please Enter Your Full Address",validators=[DataRequired()])

	state=StringField("State",validators=[DataRequired(),Length(min=1,max=50)])

	pincode=StringField("Pincode",validators=[DataRequired(),Length(min=6,max=6)])


	mobile=StringField("Mobile Number",validators=[DataRequired(),Length(min=10,max=10)])

	submit=SubmitField("Update")

	def validate_pincode(self,pincode):
		if(re.findall('\d{6}',str(pincode.data))[0]!=str(pincode.data)):
			raise ValidationError("Please enter a valid pincode")



	def validate_mobile(self,mobile):
		if(re.findall("\d{10}",str(mobile.data))[0]!=str(mobile.data)):
			raise ValidationError("Please enter a valid mobile number")



class UpdateItemForm(FlaskForm):
	name=StringField("Name",validators=[DataRequired()])

	image=FileField("Image of the Item",validators=[FileAllowed(['jpg','jpeg','png'])])

	gender=StringField("Gender Of the Item (M/F)",validators=[DataRequired(),Length(min=1,max=1)])

	size=StringField("Size of the Item if applicable",validators=[Length(min=1,max=5)])

	cost=IntegerField("Enter the Cost of the Item")

	quantity=IntegerField("Available quantity Of the item ")

	submit=SubmitField("Update")


	def validate_gender(self,gender):
		a=["M","F"]
		if gender.data not in a:
			print(gender)
			raise ValidationError("Please enter M for Male and F for Female")
