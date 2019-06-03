from checkout.db import *

from flask import Blueprint
from flask import request
from flask import jsonify

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.route("/getitem", methods=["GET"])
def get_all_item():
    """endpoint returning all items
        ---
        definitions:
          Item:
            type: object
            properties:
                sku:
                    type: string
                    example: '120P90'
                name:
                    type: string
                    example: 'Google Home'
                price:
                    type: number
                    example: 49.99
                qty:
                    type: integer
                    example: 10
          Items:
            type: array
            items:
                $ref: '#/definitions/Item'

        responses:
          200:
            description: A list of item
            schema:
              $ref: '#/definitions/Items'
            examples:
              items: [{"name": "Google Home","price": "49.99","qty": 10,"sku": "120P90"}]
        """
    items = get_db().execute(
            "SELECT * FROM item"
        ).fetchall()

    res = []
    for i in items:
        tmp = {"sku": i["sku"], "name": i["name"], "price": i["price"], "qty": i["qty"]}
        res.append(tmp)
    print(res)

    res = jsonify(res)
    res.status_code = 200
    return res


@bp.route("/additem", methods=["POST"])
def add_item():
    """endpoint adding item
        ---
        parameters:
          - name: sku
            in: formData
            description: "SKU of item"
            type: string
            required: true
          - name: name
            in: formData
            description: "name of item"
            type: string
            required: true
          - name: price
            in: formData
            description: "price of item"
            type: number
            required: true
          - name: qty
            in: formData
            description: "qty of item"
            type: integer
            required: true
        responses:
          200:
            description: success add item
        """
    try:
        sku = request.form["sku"]
        name = request.form["name"]
        price = request.form["price"]
        qty = request.form["qty"]
    except Exception:
        return jsonify(error="missing form field, must have sku, name, price, qty"), 400

    print(sku)
    db = get_db()
    error = None

    if not sku:
        error = "sku is required."
    elif not name:
        error = "name is required."
    elif not price:
        error = "price is required."
    elif not qty:
        error = "qty is required."
    elif (
            db.execute("SELECT * FROM item WHERE sku = '{}'".format(sku)).fetchone() is not None
    ):
        error = "Item {0} is already exist.".format(sku)

    print(error)
    if error is None:
        db.execute(
            "INSERT INTO item (sku, name, price, qty) VALUES (?, ?, ?, ?)", (sku, name, price, qty))
        db.commit()
        res = jsonify(success=True)
        res.status_code = 200
        return res

    res = jsonify(error=error)
    print(res)
    res.status_code = 400
    return res


class Items:
    def __init__(self):
        self.db = get_db()

    def get_all_items(self):
        items = self.db.execute(
            "SELECT * FROM item"
        ).fetchall()
        return items

    def get_item(self, sku):
        item = self.db.execute(
            "SELECT * FROM item"
            "WHERE sku = ?", sku
        ).fetchone()
        return item

    def update_item(self, sku, name, price, qty):
        self.db.execute(
            "UPDATE item SET name=?, price=?, qty=?"
            "WHERE sku=?", (name, price, qty, sku)
        )
        self.db.commit()

    def delete_item(self, sku):
        self.db.execute(
            "DELETE FROM item"
            "WHERE sku=?", sku
        )
        self.db.commit()

    def add_item(self, sku, name, price, qty):
        self.db.execute(
            "INSERT INTO item (sku, name, price, qty) VALUES (?, ?, ?, ?)", (sku, name, price, qty)
        )
        self.db.commit()
