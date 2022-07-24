from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = CHANGE_ME
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('MAP url', validators=[DataRequired(), URL()])
    img_url = StringField('IMAGE url', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    seats = IntegerField("Number of seats", validators=[DataRequired()])
    has_toilet = SelectField("Yes or No", validators=[DataRequired()], choices=["Yes", "No"])
    has_wifi = SelectField("Yes or No", validators=[DataRequired()], choices=["Yes", "No"])
    has_sockets = SelectField("Yes or No", validators=[DataRequired()], choices=["Yes", "No"])
    can_take_calls = SelectField("Yes or No", validators=[DataRequired()], choices=["Yes", "No"])
    coffee_price = StringField("Coffee price ex. $7", validators=[DataRequired()])
    submit = SubmitField('Submit')


class DeleteCafeForm(FlaskForm):
    cafe_id = IntegerField("Cafe Id", validators=[DataRequired()])
    api_key = StringField("API key to delete cafe", validators=[DataRequired()])
    submit = SubmitField('Submit')




# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()

    if form.validate_on_submit():
        print("True")
        def is_true(x):
            if x == "Yes":
                return True
            else:
                return False

        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            has_toilet=is_true(form.has_toilet.data),
            has_wifi=is_true(form.has_wifi.data),
            has_sockets=is_true(form.has_sockets.data),
            can_take_calls=is_true(form.can_take_calls.data),
            coffee_price=form.coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for("cafes"))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    all_cafes = db.session.query(Cafe).all()
    return render_template('cafes.html', cafes=all_cafes)



# # HTTP DELETE - Delete Record
@app.route('/report-closed', methods=["GET","POST"])
def delete():
    form = DeleteCafeForm()
    if form.validate_on_submit():

        if form.api_key.data == "TopSecretAPIKey":

            selected_cafe = db.session.query(Cafe).get(form.cafe_id.data)
            if selected_cafe is None:
                return render_template('status.html', status="fail: Sorry, cafe with that id was not found in the database.")
            db.session.delete(selected_cafe)
            db.session.commit()

            return render_template('status.html', status="success: Successfully deleted the new cafe.")

        else:
            return render_template('status.html', status= "fail: Sorry, that is not allowed, make sure you have the correct api-key.")

    return render_template('delete.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
