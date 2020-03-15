import json
import sqlite3
import requests
import re

from flask import Flask, g, request
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
            """CREATE TABLE IF NOT EXISTS SneakerSales
               (id integer primary key, 
               name text not null, old_price text not null,
               new_price text not null, discount text not null,
               shop text not null, sizes text not null,
               picture text not null)"""
        )
        db.commit()

        if not table_is_empty():
            return

        data = extract_data()        
        for row in data:
            query = f"""INSERT INTO SneakerSales (name, old_price, new_price, discount, shop, sizes, picture) VALUES 
                ('{row["name"]}', '{row["old_price"]}', '{row["new_price"]}', '{row["discount"]}',
                '{row["shop"]}', '{row["sizes"]}', '{row["picture"]}')"""
            cursor.execute(query)
            db.commit()


def table_is_empty():
    db_cursor = get_db().cursor()
    db_cursor.execute("SELECT * From SneakerSales")
    result = db_cursor.fetchall()
    return len(result) == 0       


def extract_data():
    data = []
    url = "https://sneaker.sale/ru/men/browse/krossovki-i-kedy/krossovki/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    products = soup.find_all("div", class_="iproduct")   
    for product in products:
        name = product.find("div", class_="iproduct__title").text[1:-1]

        price_info = product.find("div", class_="iproduct__price")
        new_price = price_info.find("span", class_="iproduct__price-current color-active").text
        old_price = price_info.find("span", class_="iproduct__price-old color-muted line-through").text
        discount = price_info.find("span", class_="discount-badge").text

        picture = product.find("div", class_="iproduct__image").find("img").get("data-src")
        shop = product.find("div", class_="iproduct__source").find("a").get("href").split("redirect/", 1)[1][:-1]

        sizes_list = []
        size_info = product.find("div", class_="iproduct__additional").find_all("span", class_=re.compile(r'btn'))
        for size in size_info:
            sizes_list.append(size.text)
        sizes = ' '.join(sizes_list)

        data_row = {
            "name": name,
            "old_price": old_price,
            "new_price": new_price,
            "discount": discount,
            "shop": shop,
            "sizes": sizes,
            "picture": picture
        }

        data.append(data_row)

    return data


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From SneakerSales")
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
    app.run()
