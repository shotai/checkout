# checkout
This project setup Endpoints for checkout demo function

# Requirements
- python 3.6
- pip
- sqlite

# Packages
- Flask
- Flasgger

# Installation
1. create virtual environment (optional)
  
        $ python -m venv venv
        $ source venv/bin/activate

2. install required python package

        $ pip install -r requirements.txt
 
3. setup flask

        $ export FLASK_APP=checkout

4. init database (optional, if you need a new database, please remove db.sqlite and run this. It will generate a new db.sqlite file)

        $ flask init-db

5. start application, default server will run at http://127.0.0.1:5000

        $ flask run

# Swagger UI
This demo contains a Swagger UI for trying out endpoint.

Once the server is running, you can find the UI at
http://127.0.0.1:5000/apidocs


# EndPoint
- /items/additem POST adding a new item

        # example request in python
        import requests

        url = "http://127.0.0.1:5000/items/additem"
        
        payload = {"sku":"123123", "name":"test", "price":2, "qty":10}
        
        response = requests.post(url, data=payload)
        
        print(response.text)
        
        # example return
        # code:200
        # {"success":true}        
        
- /items/getallitem GET returning all items
        
        # example request in python
        import requests
        
        url = "http://127.0.0.1:5000/items/getallitem/"
        
        response = requests.get(url)
        
        print(response.text)
        
        # example return
        # code:200
        # [
        #   {
        #     "name": "Google Home",
        #     "price": "49.99",
        #     "qty": 10,
        #     "sku": "120P90"
        #   }
        # ]

- /items/deleteitem/{sku} DELETE deleting item
        
        # example request in python
        import requests
        
        sku = "120P90"
        url = "http://127.0.0.1:5000/items/deleteitem/"+sku
        
        response = requests.delete(url)
        
        print(response.text)
        
        # example return
        # code:200
        # {"success":true} 

- /items/getitem/{sku} GET returning item based on sku

        # example request in python
        import requests
        
        sku = "120P90"
        url = "http://127.0.0.1:5000/items/getitem/"+sku
        
        response = requests.get(url)
        
        print(response.text)
        
        # example return
        # code:200
        #   {
        #     "name": "Google Home",
        #     "price": "49.99",
        #     "qty": 10,
        #     "sku": "120P90"
        #   }

        
- /orders/checkout/sku POST adding a new order with sku

        # example request in python
        import requests

        url = "http://127.0.0.1:5000/orders/checkout/sku"
        
        payload = {"detail":"43N23P,234234"}
        
        response = requests.post(url, data=payload)
        
        print(response.text)
        
        # example return
        # code:200
        # {
        #   "Scanned Items": "MacBook Pro,Respberry Pi B",
        #   "Total": 5399.99
        # }   

- /orders/checkout/name POST adding a new order with name

        # example request in python
        import requests

        url = "http://127.0.0.1:5000/orders/checkout/name"
        
        payload = {"detail":"MacBook Pro,Respberry Pi B"}
        
        response = requests.post(url, data=payload)
        
        print(response.text)
        
        # example return
        # code:200
        # {
        #   "Scanned Items": "MacBook Pro,Respberry Pi B",
        #   "Total": 5399.99
        # } 

- /orders/getallorder GET returning all orders

        # example request in python
        import requests

        url = "http://127.0.0.1:5000/orders/getallorder"
        
        response = requests.get(url)
        
        print(response.text)
        
        # example return
        # code:200
        # [
        #   {
        #     "created": "Mon, 03 Jun 2019 08:35:34 GMT",
        #     "scanned_items": "Respberry Pi B,MacBook Pro",
        #     "total_price": 5399.99
        #   }
        # ]

- /orders/getorder/{orderid} GET returning order based on order id

        # example request in python
        import requests
        
        order_id = "1"
        url = "http://127.0.0.1:5000/orders/getorder/"+order_id
        
        response = requests.get(url)
        
        print(response.text)
        
        # example return
        # code:200
        #   {
        #     "created": "Mon, 03 Jun 2019 08:35:34 GMT",
        #     "scanned_items": "Respberry Pi B,MacBook Pro",
        #     "total_price": 5399.99
        #   }
        