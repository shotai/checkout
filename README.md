# checkout
This project setup Endpoints for checkout demo function

# Requirements
- python 3.6
- pip

# Installation
1. create virtual environment (optional)
  
        $ python -m venv venv
        $ source venv/bin/activate

2. install required python package

        $ pip install -r requirements.txt
 
3. setup flask

        $ export FLASK_APP=checkout

4. init database (optional, if you need a new database, please run this. It will generate a new db.sqlite file)

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
        
- /items/getitem GET returning all items
- /orders/addorder POST adding a new order

        # example request in python
        import requests

        url = "http://127.0.0.1:5000/orders/addorder"
        
        payload = {"detail":"43N23P,234234"}
        
        response = requests.post(url, data=payload)
        
        print(response.text)
- /orders/getorder GET returning all orders
