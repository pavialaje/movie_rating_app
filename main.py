from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask secrete key'
app.config["SQLALCHEMY_DATABASE_URI"] = r"sqlite:///location_to_create_database\movies_collections.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app,session_options={"autoflush": False})
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique= True, nullable=False)
    year =db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250))
db.create_all()
class Edit_data(FlaskForm):
    movie_rating = StringField("Your rating out 10 eg.: 7.5", validators=[DataRequired("Do not leave blank")])
    movie_review = StringField("Your review", validators=[DataRequired()])
    subm_review = SubmitField("submit")


class Add_movie(FlaskForm):
    movie_title = StringField("Movie Name", validators=[DataRequired("Do not leave blank")])
    subm_review = SubmitField("search")

@app.route("/")
def home():
    movie_list = Movie.query.order_by(Movie.rating).all()
    movie_list.reverse()
    for i in range(len(movie_list)):
        movie_list[i].ranking = i+1
    db.session.commit()
    return render_template("index.html", movies = movie_list)

@app.route("/find")
def find():
    movie_ids = request.args.get("movie_id")
    if movie_ids:
        movie_details = requests.get(f"https://api.themoviedb.org/3/movie/{movie_ids}?api_key=010e133b740ddf113a1fbdaaa4b68ac7").json()
        new_movie = Movie(
            title= movie_details["title"],
            year=movie_details["release_date"],
            description=movie_details["overview"],
            review="",

            img_url=f'https://image.tmdb.org/t/p/w500{movie_details["poster_path"]}'
        )
        #num = new_movie.title

        db.session.add(new_movie)
        db.session.commit()
        num = new_movie.id
        #print(new_movie.id, new_movie.title)
        return redirect(url_for("edit_rating", num=num))

@app.route("/add", methods=["GET", "POST"])
def add():
    search_for_movie = Add_movie()
    if search_for_movie.validate_on_submit():
        search_movie_name = request.form["movie_title"]
        movie_data = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=your_api_key_from_website&query={search_movie_name}")
        result = movie_data.json()["results"]
        return render_template("select.html", movie_list=result)
    return render_template("add.html", search=search_for_movie)


@app.route("/edit_rating/<int:num>", methods=["GET", "POST"])
def edit_rating(num):
    movie_edit = Edit_data()
    get_movie_data = Movie.query.get(num)

    if movie_edit.validate_on_submit():
        rating = movie_edit.movie_rating.data
        review = movie_edit.movie_review.data
        get_movie_data.rating = rating
        get_movie_data.review = review
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("edit.html",movie_name=get_movie_data, edit=movie_edit)

@app.route("/delete_rating/<int:num>")
def delete_rating(num):
    get_movie_data = Movie.query.get(num)
    db.session.delete(get_movie_data)
    db.session.commit()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
