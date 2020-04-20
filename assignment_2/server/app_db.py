import json
import sqlite3
import requests
import re

from flask import Flask, g
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS FarfetchSneakers
               (id integer primary key, 
               brand text not null, description text not null,
               price text not null, discount text not null,
               href text not null, picture_first text not null,
               picture_second text not null)"""
        )
        db.commit()


def extract_data():
    data = []
    
    url = "https://www.farfetch.com/ru/shopping/men/trainers-2/items.aspx?view=180&scale=282"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    products = soup.find_all("li", attrs={"data-test": "productCard"})

    for product in products:
        brand = product.find("h3", attrs={"data-test": "productDesignerName"}).text
        description = product.find("p", attrs={"data-test": "productDescription"}).text.replace("\'", "")

        price = product.find("span", attrs={"data-test": "price"}).text

        discount = product.find("span", attrs={"data-test": "discountPercentage"})
        if (discount is None):
            discount = "No discount"
        else:
            discount = discount.text

        href = "https://www.farfetch.com/ru" + product.find("a", class_="_6871ed").get("href")
        pictures = [image.get("content") for image in product.find_all("meta", attrs={"itemprop": "image"})]
        picture_first = pictures[0]
        picture_second = pictures[1]

        id = int(''.join(re.findall(r'\d+', href)))

        data_row = {
            "id": id,
            "brand": brand,
            "description": description,
            "price": price,
            "discount": discount,
            "href": href,
            "picture_first": picture_first,
            "picture_second": picture_second
        }

        data.append(data_row)

    return data


def add_content():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        data = extract_data()        
        for row in data:
            query = f"""REPLACE INTO FarfetchSneakers (id, brand, description, price, discount, href, picture_first, picture_second) VALUES 
                ('{row["id"]}', '{row["brand"]}', '{row["description"]}', '{row["price"]}', '{row["discount"]}',
                '{row["href"]}', '{row["picture_first"]}', '{row["picture_second"]}')"""
            cursor.execute(query)
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From FarfetchSneakers")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    add_content()
    app.run()
