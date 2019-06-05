from checkout.db import *
from flask import Blueprint
from flask import request
from flask import jsonify
import collections

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/checkout/sku", methods=["POST"])
def checkout_sku():
    """endpoint checkout
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
            examples: {'Scanned Items': 'MacBook Pro,Respberry Pi B','Total': 5399.99}

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

    if error is None:
        scanned_items, total_price = checkout(detail, db)

        # return response
        res = jsonify({"Scanned Items": ",".join(scanned_items), "Total": total_price})
        res.status_code = 200
        return res

    # error response
    res = jsonify(error=error)
    res.status_code = 400
    return res


@bp.route("/checkout/name", methods=["POST"])
def checkout_name():
    """endpoint checkout
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
            description: "name of scanned items, separate by comma"
            type: string
            example: 'MacBook Pro,Respberry Pi B'
            required: true

        responses:
          200:
            description: success add order
            schema:
              $ref: '#/definitions/Brief'
            examples: {'Scanned Items': 'MacBook Pro,Respberry Pi B','Total': 5399.99}

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

    if error is None:
        scanned_items, total_price = checkout(detail, db, True)
        if not total_price:
            return jsonify(error=scanned_items), 400

        # return response
        res = jsonify({"Scanned Items": ",".join(scanned_items), "Total": total_price})
        res.status_code = 200
        return res

    # error response
    res = jsonify(error=error)
    res.status_code = 400
    return res


@bp.route("/getallorder", methods=["GET"])
def get_all_orders():
    """endpoint returning all orders
        ---
        definitions:
          Order:
            type: object
            properties:
                id:
                    type: integer
                    example: '1'
                created:
                    type: string
                    example: 'Mon, 03 Jun 2019 08:35:34 GMT'
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
            "SELECT id, created,  item_names, total_price FROM online_order"
        ).fetchall()

    res = []
    for i in items:
        tmp = {"id": i["id"], "created": i["created"], "scanned_items": i["item_names"], "total_price": i["total_price"]}
        res.append(tmp)
    print(res)

    res = jsonify(res)
    res.status_code = 200
    return res


@bp.route("/getorder/<int:orderid>", methods=["GET"])
def get_order(orderid):
    """endpoint returning order with id
        ---
        definitions:
          Order:
            type: object
            properties:
                id:
                    type: integer
                    example: '1'
                created:
                    type: string
                    example: 'Mon, 03 Jun 2019 08:35:34 GMT'
                scanned_items:
                    type: string
                    example: 'Google Home'
                total_price:
                    type: number
                    example: 49.99

        parameters:
          - name: orderid
            in: path
            description: "id of order"
            type: string
            example: '2'
            required: true

        responses:
          200:
            description: A Order
            schema:
              $ref: '#/definitions/Order'
            examples:
              items: {'created': 'Mon, 03 Jun 2019 08:35:34 GMT','scanned_items': 'Respberry Pi B,MacBook Pro','total_price': 5399.99}
        """
    sql = "SELECT id, created,  item_names, total_price FROM online_order where id={}".format(orderid)
    item = get_db().execute(sql).fetchone()

    res = {"id": item["id"], "created": item["created"], "scanned_items": item["item_names"], "total_price": item["total_price"]}
    print(res)

    res = jsonify(res)
    res.status_code = 200
    return res


def checkout(detail, db, use_name=False):
    tmp_cart = collections.defaultdict(int)

    scanned_items = []

    for i in detail.split(","):
        tmp_cart[i] += 1

    # dealing with free item
    if use_name:
        main_one = "MacBook Pro"
        free_one = "Respberry Pi B"
    else:
        main_one = "43N23P"
        free_one = "234234"
    free_item_num = -1
    if main_one in tmp_cart:
        free_item_num = tmp_cart[main_one]
        if free_one not in tmp_cart or tmp_cart[free_one] < tmp_cart[main_one]:
            tmp_cart[free_one] = tmp_cart[main_one]

    # check inventory see if they could full fill the order
    tmp = ",".join("'{}'".format(w) for w in tmp_cart.keys())
    if use_name:
        sql = "SELECT * FROM item WHERE name in ({}) order by name".format(tmp)
    else:
        sql = "SELECT * FROM item WHERE sku in ({}) order by name".format(tmp)
    rows = db.execute(sql).fetchall()
    items = {}

    cart = {}
    # if use name, rebuild cart with sku
    if use_name:
        for r in rows:
            tmp = tmp_cart[r["name"]]
            cart[r["sku"]] = tmp
    else:
        cart = tmp_cart

    # checking inventory
    for r in rows:
        items[r["sku"]] = (r["name"], r["price"], r["qty"])
        if cart[r["sku"]] > r["qty"]:
            if r["sku"] == "234234" and free_item_num > 0:
                continue
            return "cannot full fill the order, {} is not enough".format(r["name"]), None

    # calculating total price
    total_price = 0
    update_info = {}

    for sku, order_num in cart.items():
        name, price, qty = items[sku]
        if sku == "120P90":
            total_price += ((order_num // 3) * price * 2) + (order_num % 3 * price)
        elif sku == "A304SD" and order_num >= 3:
            total_price += price * order_num * 0.9
        elif sku == "234234" and free_item_num > 0:
            if free_item_num > qty:
                order_num = qty
            if order_num - free_item_num > 0:
                total_price += price * (order_num - free_item_num)
        else:
            total_price += price * order_num

        update_info[sku] = (name, price, qty - order_num, order_num)

    # update inventory
    for sku, tmp in update_info.items():
        name, price, num, order_num = tmp

        for _ in range(order_num):
            scanned_items.append(name)

        sql = "UPDATE item SET name='{0}', price={1}, qty={2} WHERE sku='{3}'".format(name, price,
                                                                                      num,
                                                                                      sku)
        print(sql)
        db.execute(sql)
        db.commit()

    # save order info
    total_price = round(total_price, 2)
    db.execute(
        "INSERT INTO online_order (detail, item_names, total_price) VALUES (?, ?, ?)",
        (detail, ",".join(scanned_items), total_price))
    db.commit()
    return scanned_items, total_price
