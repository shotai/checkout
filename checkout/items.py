from checkout.db import *

from flask import Blueprint
from flask import request
from flask import jsonify

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.route("/getallitem", methods=["GET"])
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


@bp.route("/getitem/<string:sku>", methods=["GET"])
def get_item(sku):
    """endpoint returning item based on sku
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
        parameters:
          - name: sku
            in: path
            description: "SKU of item"
            type: string
            required: true
        responses:
          200:
            description: An item
            schema:
              $ref: '#/definitions/Item'
            examples:
              items: {"name": "Google Home","price": "49.99","qty": 10,"sku": "120P90"}
        """
    sql = "SELECT * FROM item where sku='{}'".format(sku)
    item = get_db().execute(sql).fetchone()

    res = {"sku": item["sku"], "name": item["name"], "price": item["price"], "qty": item["qty"]}
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


@bp.route("/updateitem/<string:sku>", methods=["UPDATE", "POST"])
def update_item(sku):
    """endpoint updating item
        ---
        parameters:
          - name: sku
            in: path
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
            description: success update item
        """
    try:
        name = request.form["name"]
        price = request.form["price"]
        qty = request.form["qty"]
    except Exception:
        return jsonify(error="missing field, must have sku, name, price, qty"), 400

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
            db.execute("SELECT * FROM item WHERE sku = '{}'".format(sku)).fetchone() is None
    ):
        error = "Item {0} is not exist.".format(sku)

    print(error)
    if error is None:
        sql = "UPDATE item SET name='{0}', price={1}, qty={2} WHERE sku={3}".format(name, price, qty, sku)
        db.execute(sql)
        db.commit()
        res = jsonify(success=True)
        res.status_code = 200
        return res

    res = jsonify(error=error)
    print(res)
    res.status_code = 400
    return res


@bp.route("/deleteitem/<string:sku>", methods=["DELETE"])
def delete_item(sku):
    """endpoint deleting item
        ---
        parameters:
          - name: sku
            in: path
            description: "SKU of item"
            type: string
            required: true
        responses:
          200:
            description: success delete item
        """
    print(sku)
    db = get_db()
    error = None

    if not sku:
        error = "sku is required."
    elif (
            db.execute("SELECT * FROM item WHERE sku = '{}'".format(sku)).fetchone() is None
    ):
        error = "Item {0} is not exist.".format(sku)

    print(error)
    if error is None:
        sql = "DELETE item WHERE sku={0}".format(sku)
        db.execute(sql)
        db.commit()
        res = jsonify(success=True)
        res.status_code = 200
        return res

    res = jsonify(error=error)
    print(res)
    res.status_code = 400
    return res
