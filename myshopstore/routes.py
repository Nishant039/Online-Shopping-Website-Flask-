from myshopstore import app
from flask import render_template
from flask import url_for,redirect
from flask import flash
from myshopstore.models import User,Item,Association,Info
from myshopstore import db
from myshopstore.forms import RegistrationForm,LoginForm,ItemForm,AddressForm,UpdateItemForm
from myshopstore import bcrypt

from flask_login import login_user,logout_user,current_user,login_required
from flask import request
import os
from PIL import Image
import secrets

from flask import current_app
from flask import abort
from flask_mail import Message

from myshopstore import mail

import smtplib

@app.route("/home")
@app.route("/")
def home():
	items=Item.query.all()
	return render_template('home.html',title="Home",items=items)


@app.route("/register",methods=["GET","POST"])
def register():
	form=RegistrationForm()
	if(form.validate_on_submit()):
		hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User(username=form.username.data,email=form.email.data,password=hashed_password)
		db.session.add(user)
		db.session.commit()

		flash(f'Account created for {form.username.data} !','success')
		return redirect(url_for('home'))

	return render_template('register.html',title="Register",form=form)


@app.route("/login",methods=["GET","POST"])
def login():
	form=LoginForm()
	if(form.validate_on_submit()):
		user=User.query.filter_by(email=form.email.data).first()
		if(user and bcrypt.check_password_hash(user.password,form.password.data)):
			login_user(user)
			next_page=request.args.get('next')
			flash(f'Logged in as {current_user.username.title()}','success')

			return redirect(next_page) if next_page else redirect(url_for('home'))

		else:
			flash(f'Invalid Credentials please try again','danger')


	return render_template('login.html',title="Login",form=form)


@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash('Logged out successfully','success')
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex=secrets.token_hex(8)
	fname,fext=os.path.splitext(form_picture.filename)
	picture_fn=random_hex+fext
	picture_path=os.path.join(current_app.root_path,'static/itemicon',picture_fn)

	output_size=(256,256)
	i=Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)
	return picture_fn



@app.route("/additem",methods=["GET","POST"])
@login_required
def additem():
	if (current_user.email!="jo.supplier1@gmail.com"):

		abort(403)
	form=ItemForm()
	if(form.validate_on_submit()):
		if(form.image.data):
			image_path=save_picture(form.image.data)


			item=Item(name=form.name.data,
			size=form.size.data,
			gender=form.gender.data,
			cost=form.cost.data,
			quantity=form.quantity.data,
			image=image_path)
		else:
			item=Item(name=form.name.data,
			size=form.size.data,
			gender=form.gender.data,
			cost=form.cost.data,
			quantity=form.quantity.data)

		db.session.add(item)
		db.session.commit()
		flash(f"Successfully Added Item {form.name.data}",'success')

		return redirect(url_for('home'))


	return render_template('additem.html',title="Add Item",form=form)


@app.route("/addcart/<int:item_id>",methods=["POST"])
@login_required
def addcart(item_id):
	# print(item_id)
	item=Item.query.get_or_404(item_id)
	# print(item)
	quantity=int(request.form['quantity'])
	# print(quantity)
	# print(item.quantity)
	if(quantity==0):
		return redirect(url_for('home'))
	if(quantity>item.quantity):
		flash("Total Quantity in your cart will exceed what is available !",'info')
		return redirect(url_for('home'))
	else:
		for present_item in current_user.items:
			if(item==present_item.item):
				if((present_item.quant+quantity)<=item.quantity):
					present_item.quant=present_item.quant+quantity
					db.session.commit()
					flash("Item added successfully to cart !",'success')
					return redirect(url_for('home'))
				else:
					flash("Total Quantity in your cart will exceed what is available !",'info')
					return redirect(url_for('home'))

		ass=Association(item,current_user,quantity)
		db.session.add(ass)
		db.session.commit()

		flash("Item added successfully to cart !",'success')

		return redirect(url_for('home'))


@app.route("/cart",methods=["GET","POST"])
@login_required
def cart():
	associated_items=current_user.items
	total=0
	return render_template('cart.html',title="Your Cart",associated_items=associated_items)



@app.route("/minuscart/<int:item_id>",methods=["GET","POST"])
def minuscart(item_id):
	ass=Association.query.filter_by(user_id=current_user.id,item_id=item_id).first()
	if(ass.quant<=1):
		db.session.delete(ass)
		db.session.commit()
	else:
		ass.quant=ass.quant-1
		db.session.commit()
	return redirect(url_for('cart'))

@app.route("/pluscart/<int:item_id>",methods=["GET","POST"])
def pluscart(item_id):
	item=Item.query.get(item_id)
	ass=Association.query.filter_by(user_id=current_user.id,item_id=item_id).first()
	if(ass.quant+1>item.quantity):
		flash("Total Quantity is exceeding available quantity",'warning')
		return redirect(url_for('cart'))

	else:
		ass.quant=ass.quant+1
		db.session.commit()
	return redirect(url_for('cart'))


@app.route("/address/",methods=["GET","POST"])
def address():
	form=AddressForm()
	if(request.method=="GET"):
		if(current_user.infos):
			form.state.data=current_user.infos[0].state
			form.address.data=current_user.infos[0].address
			form.pincode.data=current_user.infos[0].pincode
			form.mobile.data=current_user.infos[0].mobile_number

		return render_template("address.html",title="Address Info",form=form)
	elif(request.method=="POST"):
		if(form.validate_on_submit()):
			if(current_user.infos):
				info=Info.query.filter_by(user_id=current_user.id).first()
				info.address=form.address.data
				info.mobile=form.mobile.data
				info.pincode=form.pincode.data
				info.state=form.state.data
				db.session.commit()
				flash("Address Updated Suceessfully","success")
				return redirect(url_for("home"))	
			else:
				info=Info(user_id=current_user.id,state=form.state.data,pincode=form.pincode.data,address=form.address.data,mobile_number=form.mobile.data)
				db.session.add(info)
				db.session.commit()
				flash("Address Updated Suceessfully","success")
				return redirect(url_for("home"))


def send_mail(user):
	items=current_user.items
	item_names=[]
	quantity=[]
	total_cost=0
	for ass_item in items:
		item_names.append(ass_item.item.name)
		quantity.append(ass_item.quant)
		print(ass_item.item.name,ass_item.quant)
		total_cost=total_cost+ass_item.item.cost*ass_item.quant

	EMAIL="myshopstoremail@gmail.com"
	PASSWORD="Nishant@1908"	
	with smtplib.SMTP("smtp.gmail.com",587) as smtp:
		smtp.ehlo()
		smtp.starttls()
		smtp.ehlo()

		smtp.login(EMAIL,PASSWORD)

		SUBJECT="ORDER CONFIRMATION !"
		BODY=f"Your order for {item_names} with respective quantitites {quantity} . Please keep an amount of {total_cost} with you !"

		msg=f'Subject : {SUBJECT}\n\n{BODY}'	
		

		smtp.sendmail(EMAIL,user.email,msg)



	
@app.route("/commitorder",methods=["GET","POST"])
def commitorder():

	send_mail(current_user)

	associated_items=current_user.items

	for item in associated_items:
		item.item.quantity=item.item.quantity-1
		db.session.delete(item)

	db.session.commit()

	return redirect(url_for("home"))



@app.route("/update/<int:id>",methods=["GET","POST"])
@login_required
def updateitem(id):
	if(current_user.email!="jo.supplier1@gmail.com"):
		abort(403)
	else:
		form=UpdateItemForm()
		item=Item.query.get_or_404(id)
		if(request.method=="GET"):
			form.name.data=item.name
			form.gender.data=item.gender
			form.size.data=item.size
			form.quantity.data=item.quantity
			form.cost.data=item.cost
			return render_template("updateitem.html",title="Update Item",form=form)

		elif(request.method=="POST"):
			if(form.image.data):
				image_path=save_picture(form.image.data)
				item.name=form.name.data
				item.gender=form.gender.data
				item.size=form.size.data
				item.quantity=form.quantity.data
				item.cost=form.cost.data
				item.image=image_path
				
			else:
				item.name=form.name.data
				item.gender=form.gender.data
				item.size=form.size.data
				item.quantity=form.quantity.data
				item.cost=form.cost.data				
			

			db.session.commit()
			flash("Item updated Successfully",'success')
			return redirect(url_for('home'))


		
