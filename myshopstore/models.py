from myshopstore import db

from myshopstore import login_manager
from flask_login import UserMixin

from sqlalchemy.ext.associationproxy import association_proxy


# relationship_table=db.Table('relationship_table',
# 	db.Column('user_id',db.Integer,db.ForeignKey('user.id'),nullable=False),
# 	db.Column('item_id',db.Integer,db.ForeignKey('item.id'),nullable=False),
# 	db.PrimaryKeyConstraint('user_id','item_id'))

class Association(db.Model):
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)

	item_id=db.Column(db.Integer,db.ForeignKey('item.id'),primary_key=True)

	quant=db.Column(db.Integer)

	item=db.relationship("Item")

	customer=db.relationship("User",backref="items")


	def __init__(self,item,customer,quantity):
		self.item=item
		self.customer=customer
		self.quant=quantity

	def __repr__(self):
		return f"Association('{self.user_id}','{self.item_id}','{self.quant}')"

	
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
class User(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(20),unique=True,nullable=False)
	email=db.Column(db.String(120),unique=True,nullable=False)

	password=db.Column(db.String(60),nullable=False)

	# items=db.relationship('Association',backref='customer')

	infos=db.relationship('Info',backref='owner',lazy=True)

	def __init__(self,username,email,password):
		self.username=username
		self.email=email
		self.password=password


	def __repr__(self):
		return f"User('{self.username}','{self.email}')"

class Item(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(120),nullable=False)
	image=db.Column(db.String(20),nullable=False,default='default.jpg')
	gender=db.Column(db.String(1),nullable=False)
	size=db.Column(db.String(5),nullable=False)
	cost=db.Column(db.Integer)
	quantity=db.Column(db.Integer,nullable=False)

	# customers=db.relationship("Association",backref="item")


	def __init__(self,name,gender,size,cost,quantity,image="default.jpg"):
		self.name=name
		self.gender=gender
		self.size=size
		self.cost=cost
		self.quantity=quantity
		self.image=image

	def __repr__(self):
		return f"Item('{self.name}','{self.image}','{self.cost}')"

class Info(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
	state=db.Column(db.String(50),nullable=False)

	pincode=db.Column(db.String(10),nullable=False)

	address=db.Column(db.Text,nullable=False)

	mobile_number=db.Column(db.String(10),nullable=False)

	def __repr__(self):
		return f"Info('{self.address}','{self.mobile_number}')"

