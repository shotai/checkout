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

    cart = collections.defaultdict(int)

    scanned_items = []
    if error is None:
        for i in detail.split(","):
            cart[i] += 1

        # dealing with free item
        free_item_num = -1
        if "43N23P" in cart:
            free_item_num = cart["43N23P"]
            if "234234" not in cart or cart["234234"] < cart["43N23P"]:
                cart["234234"] = cart["43N23P"]
        print(free_item_num)
        print(cart)

        # check inventory see if they could full fill the order
        tmp = ",".join("'{}'".format(w) for w in cart.keys())
        sql = "SELECT * FROM item WHERE sku in ({}) order by name".format(tmp)
        rows = db.execute(sql).fetchall()
        items = {}
        for r in rows:
            items[r["sku"]] = (r["name"], r["price"], r["qty"])
            if cart[r["sku"]] > r["qty"]:
                if r["sku"] == "234234" and free_item_num > 0:
                    continue
                return jsonify(error="cannot full fill the order, {} is not enough".format(r["name"])), 400
        print(items)

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
                    total_price += price * (order_num-free_item_num)
            else:
                total_price += price * order_num

            update_info[sku] = (name, price, qty-order_num, order_num)

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
