from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///countries.db"
db = SQLAlchemy(app)


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cca3 = db.Column(db.String(3), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)
    currency = db.Column(db.String(50), nullable=False)
    capital = db.Column(db.String(50))
    region = db.Column(db.String(50))
    subregion = db.Column(db.String(50))
    area = db.Column(db.BigInteger)
    map_url = db.Column(db.String(255))
    population = db.Column(db.BigInteger)
    flag_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    neighbours = db.relationship('Neighbour', backref='country', lazy=True)

class Neighbour(db.Model):
    __tablename__ = 'neighbours'
    id = db.Column(db.Integer, primary_key=True)
    neighbour_country_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)


@app.route('/country', methods=['GET'])
def get_all_countries():
    sort_by = request.args.get('sort_by', 'a_to_z')  
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    query = Country.query

    if sort_by == 'a_to_z':
        query = query.order_by(Country.name.asc())
    elif sort_by == 'z_to_a':
        query = query.order_by(Country.name.desc())
    elif sort_by == 'population_high_to_low':
        query = query.order_by(Country.population.desc())
    elif sort_by == 'population_low_to_high':
        query = query.order_by(Country.population.asc())
    elif sort_by == 'area_high_to_low':
        query = query.order_by(Country.area.desc())
    elif sort_by == 'area_low_to_high':
        query = query.order_by(Country.area.asc())
    
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    countries_list = []
    for country in pagination.items:
        countries_list.append({
            "id": country.id,
            "name": country.name,
            "cca3": country.cca3,
            "currency_code": country.currency_code,
            "currency": country.currency,
            "capital": country.capital,
            "region": country.region,
            "subregion": country.subregion,
            "area": country.area,
            "map_url": country.map_url,
            "population": country.population,
            "flag_url": country.flag_url
        })
    
    return jsonify({
        "message": "Country list",
        "data": {
            "list": countries_list,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "page": pagination.page,
            "pages": pagination.pages,
            "per_page": pagination.per_page,
            "total": pagination.total
        }
    }), 200

@app.route('/country/<int:id>/neighbour', methods=['GET'])
def get_country_neighbours(id):
    country = Country.query.get(id)
    if country is None:
        return jsonify({"message": "Country not found", "data": {}}), 404

    neighbours = Neighbour.query.filter_by(country_id=id).all()
    neighbour_countries = []

    for neighbour in neighbours:
        neighbour_country = Country.query.get(neighbour.neighbour_country_id)
        if neighbour_country:
            neighbour_countries.append({
                "id": neighbour_country.id,
                "name": neighbour_country.name,
                "cca3": neighbour_country.cca3,
                "currency_code": neighbour_country.currency_code,
                "currency": neighbour_country.currency,
                "capital": neighbour_country.capital,
                "region": neighbour_country.region,
                "subregion": neighbour_country.subregion,
                "area": neighbour_country.area,
                "map_url": neighbour_country.map_url,
                "population": neighbour_country.population,
                "flag_url": neighbour_country.flag_url
            })
       
    return jsonify({
        "message": "Country neighbours",
        "data": {"countries": neighbour_countries}
    }), 200



@app.route("/country/<int:id>", methods=["GET"])
def country_by_id(id):
    country = Country.query.get(id)
    if country is None:
        return jsonify({"message": "Country not found", "data": {}}), 404
    country_data = {
        "id": country.id,
        "name": country.name,
        "cca3": country.cca3,
        "currency_code": country.currency_code,
        "currency": country.currency,
        "capital": country.capital,
        "region": country.region,
        "subregion": country.subregion,
        "area": country.area,
        "map_url": country.map_url,
        "population": country.population,
        "flag_url": country.flag_url
    }

    return jsonify({
        "message": "country details",
        "data": {
            "country": country_data
        }
    }),200

if __name__ == '__main__':
    app.run(debug=True, port=8000)
