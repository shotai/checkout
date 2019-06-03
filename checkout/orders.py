from checkout.db import *
from flask import Blueprint
from flask import request
from flask import jsonify
import collections

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/addorder", methods=["POST"])
def add_item():
    """endpoint adding order
        ---
        definitions:
          Brief:
            type: object
            properties:
                "Scanned Items":
                    type: string
                    example: 'Respberry Pi B,MacBook Pro'
                Total:
                    type: number
                    example: 5399.99
        parameters:
          - name: detail
            in: formData
            description: "SKU of scanned items, separate by comma"
            type: string
            example: '43N23P,234234'
            required: true

        responses:
          200:
            description: success add order
            schema:
              $ref: '#/definitions/Brief'
            examples: {'Scanned Items': 'Respberry Pi B,MacBook Pro','Total': 5399.99}

        """
    try:
        detail = request.form["detail"]
    except Exception:
        return jsonify(error="missing form field, must have detail"), 400

    print(detail)
    db = get_db()
    error = None

    if not detail:
        error = "detail is required."

    cart = collections.defaultdict(int)
    tmp = ",".join("'{}'".format(w) for w in detail.split(","))
    scanned_items = []
    if error is None:

        for i in detail.split(","):
            cart[i] += 1

        total_price = 0
        sql = "SELECT * FROM item WHERE sku in ({}) order by name".format(tmp)
        print(sql)
        item_rows = db.execute(sql).fetchall()

        for r in item_rows:
            if r["qty"] < cart[r["sku"]]:
                return jsonify(error="cannot full fill the order, {} is not enough".format(r["name"])), 400
            elif r["sku"] == "234234":
                if "43N23P" in cart:
                    total_price += (cart[r["sku"]] - cart["43N23P"]) * r["price"]
                else:
                    total_price += r["price"] * cart[r["sku"]]
            elif r["sku"] == "120P90":
                total_price += ((cart[r["sku"]] // 3) * r["price"] * 2) + (cart[r["sku"]] % 3 * r["price"])
            elif r["sku"] == "A304SD" and cart[r["sku"]] >= 3:
                total_price += r["price"] * cart[r["sku"]] * 0.9
            else:
                total_price += r["price"] * cart[r["sku"]]
            scanned_items.append(r["name"])

            sql = "UPDATE item SET name='{0}', price={1}, qty={2} WHERE sku='{3}'".format(r["name"], r["price"],
                                                                                          r["qty"] - cart[r["sku"]],
                                                                                          r["sku"])
            print(sql)
            db.execute(sql)
            db.commit()
        total_price = round(total_price, 2)
        db.execute(
            "INSERT INTO online_order (detail, item_names, total_price) VALUES (?, ?, ?)",
            (detail, ",".join(scanned_items), total_price))
        db.commit()
        res = jsonify({"Scanned Items": ",".join(scanned_items), "Total": total_price})
        res.status_code = 200
        return res

    res = jsonify(error=error)
    res.status_code = 400
    return res


@bp.route("/getorder", methods=["GET"])
def get_all_orders():
    """endpoint returning all orders
        ---
        definitions:
          Order:
            type: object
            properties:
                created:
                    type: string
                    example: '1'
                scanned_items:
                    type: string
                    example: 'Google Home'
                total_price:
                    type: number
                    example: 49.99
          Orders:
            type: array
            items:
                $ref: '#/definitions/Order'

        responses:
          200:
            description: A list of Order
            schema:
              $ref: '#/definitions/Orders'
            examples:
              items: [{'created': 'Mon, 03 Jun 2019 08:35:34 GMT','scanned_items': 'Respberry Pi B,MacBook Pro','total_price': 5399.99}]
        """
    items = get_db().execute(
            "SELECT created,  item_names, total_price FROM online_order"
        ).fetchall()

    res = []
    for i in items:
        tmp = {"created": i["created"], "scanned_items": i["item_names"], "total_price": i["total_price"]}
        res.append(tmp)
    print(res)

    res = jsonify(res)
    res.status_code = 200
    return res

class Orders:
    def __init__(self):
        self.db = get_db()

    def get_all_orders(self):
        orders = self.db.execute(
            "SELECT * FROM online_order"
        ).fetchall()

        return orders

    def get_order(self, order_id):
        order = self.db.execute(
            "SELECT * FROM online_order"
            "WHERE id = ?", order_id
        ).fetchone()
        return order

    def update_order(self, detail, order_id):
        self.db.execute(
            "UPDATE online_order SET detail=?"
            "WHERE id=?", (detail, order_id)
        )
        self.db.commit()

    def delete_order(self, order_id):
        self.db.execute(
            "DELETE FROM online_order"
            "WHERE id=?", order_id
        )
        self.db.commit()

    def add_order(self, detail):
        self.db.execute(
            "INSERT INTO online_order (detail) VALUES (?)", detail
        )
        self.db.commit()
