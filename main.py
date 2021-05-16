from fastapi import FastAPI, Request, status, HTTPException, Depends, Cookie
import hashlib
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from typing import Optional
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import random
import sqlite3
from router import router as northwind_api_router






app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(northwind_api_router, tags=["northwind"])

security = HTTPBasic()
app.secret_key = "bardzodlugiciagznakowktorychrzeczjasnaniemoznanikomupodawacxd"
app.token = []
app.session = []

class Pacjent(BaseModel):
	id: Optional[int] = None
	name: str
	surname: str
	register_date: Optional[date] = None
	vaccination_date: Optional[date] = None


class Category_Class(BaseModel):
	name: str



pacjenci = []


app.newuser_id = 1

@app.get("/")
def root():
    return {"message": "Hello world"}

#-----------------ZADANIA 1.X-----------------------------------------------------------------


@app.get("/hello/{name}")
async def hello_name_view(name: str):
    return f"Hello {name}"


@app.get("/method", status_code=200)
def metoda_requestu(request: Request, response:Response):
    return {"method": request.method}

@app.post("/method", status_code=201)
def metoda_requestu_post(request: Request, response:Response):
    return {"method": request.method}

@app.delete("/method", status_code=200)
def metoda_requestu(request: Request, response:Response):
    return {"method": request.method}

@app.put("/method", status_code=200)
def metoda_requestu(request: Request, response:Response):
    return {"method": request.method}

@app.options("/method", status_code=200)
def metoda_requestu(request: Request, response:Response):
    return {"method": request.method}   


@app.get("/auth")
def pass_verification(password: str, password_hash: str, response: Response):
	password = password.encode()  #zmiana na utf 8, zeby dalo sie zahaszowac
	if not password:
		raise HTTPException(status_code=401)		
	
	h = hashlib.sha512(password)	
	if h.hexdigest()==password_hash:
		raise HTTPException(status_code=204)
	else:
		raise HTTPException(status_code=401)
	return response.status_code

@app.post("/register")
def add_user(pacjent: Pacjent, response:Response, request:Request):	
	nID = app.newuser_id
	app.newuser_id +=1
	pacjent.id = nID

	nData = date.today()
	pacjent.register_date = nData

	ilosc_liter_w_imieniu = sum(c.isalpha() for c in pacjent.name)
	ilosc_liter_w_nazwisku = sum(c.isalpha() for c in pacjent.surname)
	




	nVData = nData + timedelta(ilosc_liter_w_imieniu+ilosc_liter_w_nazwisku)
	pacjent.vaccination_date = nVData
	
	pacjenci.append(pacjent) 
	response.status_code = status.HTTP_201_CREATED
	return pacjent


@app.get("/patient/{id}", response_model=Pacjent)
def wyswietlanie_pacjentow(id: int):
	if id < 1:
		raise HTTPException(status_code=400)
	for i in pacjenci:
		if i.id==id:
			return i
	else:
		raise HTTPException(status_code=404)

	
@app.get("/hello", response_class=HTMLResponse)
def hello_date_html(request:Request):
	dzisiaj = date.today()
	return templates.TemplateResponse("hello.html.j2", {"request": request, "curr_date":dzisiaj})



#--------------SEJSA I COOKIES + TOKENY (ZADANIA 3.X)-------------------------------------------------------------

def new_token(username, password):
	creation_time = str(datetime.now())
	new = hashlib.sha256(str(username+password+app.secret_key+creation_time).encode()).hexdigest()
	return new


@app.post("/login_session", status_code=201)
def login_session(response:Response, creds: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(creds.username, "4dm1n")
	correct_password = secrets.compare_digest(creds.password, "NotSoSecurePa$$")
	if not (correct_username and correct_password):
		raise HTTPException(status_code=401)
	else:
		session_token = new_token(creds.username, creds.password)
		app.session.append(session_token)
		if len(app.session)>3:
			app.session.pop(0)
		response.set_cookie(key="session_token", value = session_token) #set cookie

		


@app.post("/login_token")
def login_token(response:Response, creds: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(creds.username, "4dm1n")
	correct_password = secrets.compare_digest(creds.password, "NotSoSecurePa$$")
	if not (correct_username and correct_password):
		raise HTTPException(status_code=401)
	else:
		token_value = new_token(creds.username,creds.password)
		app.token.append(token_value)
		if len(app.token)>3:
			app.token.pop(0)
		return JSONResponse(status_code = status.HTTP_201_CREATED, content= {"token":token_value})


@app.get("/welcome_session")
def welcome_session(request:Request, format = ""):
	session_token = request.cookies.get("session_token") #get cookie
	if  session_token not in app.session or not session_token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	else:
		if format == 'json':
			return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Welcome!"})
		elif format == 'html':
			return HTMLResponse(status_code=status.HTTP_200_OK, content = '<h1>Welcome!</h1>')

		else:
			return PlainTextResponse(status_code=status.HTTP_200_OK, content = 'Welcome!')

@app.get("/welcome_token")
def welcome_token(token = "", format = ""):
	if token not in app.token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
	else:
		if format == 'json':
			return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Welcome!"})
		elif format == 'html':
			return HTMLResponse(status_code=status.HTTP_200_OK, content = '<h1>Welcome!</h1>')
		else:
			return PlainTextResponse(status_code=status.HTTP_200_OK, content = 'Welcome!')

@app.get("/logged_out")
def logged_out(format= ""):
	if format == 'json':
			return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Logged out!"})
	elif format == 'html':
			return HTMLResponse(status_code=status.HTTP_200_OK, content = '<h1>Logged out!</h1>')
	else:
			return PlainTextResponse(status_code=status.HTTP_200_OK, content = 'Logged out!')


@app.delete("/logout_session")
def logout_session(request:Request, format = ""):
    session_token = request.cookies.get("session_token")
    if session_token not in app.session or not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        app.session.remove(session_token)
        return RedirectResponse(status_code=303, url="/logged_out?format="+format)


@app.delete("/logout_token")
def logout_token(token = "", format = ""):
    if token not in app.token or token=="":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        app.token.remove(token)
        return RedirectResponse(status_code=303, url="/logged_out?format="+format)
       


#--------------------------SQLite (Zadania 4.X)-------------------------------------------------
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")

@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

@app.get("/categories", status_code=200)
async def categories():
	cursor = app.db_connection.cursor()
	cursor.row_factory = sqlite3.Row
	categories = cursor.execute("""
		SELECT CategoryID, CategoryName From Categories ORDER BY CategoryID
		""").fetchall()
	return {
	"categories": [{"id": x["CategoryID"], "name": x["CategoryName"]} for x in categories]
	}

@app.get("/customers", status_code=200)
async def customers():
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    customers = cursor.execute("""

    SELECT CustomerID, CompanyName, COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || COALESCE(Country, '') As FullAddress
    FROM Customers
    ORDER BY CustomerID;

    """).fetchall()
    
    return {
    "customers": [{"id": x["CustomerID"],"name": x["CompanyName"],"full_address": x["FullAddress"]} for x in customers]
    }
    
	





@app.get("/products/{id}")
async def products(id: int):
	app.db_connection.row_factory = sqlite3.Row
	cursor = app.db_connection.cursor()
	product = cursor.execute("""
		SELECT ProductID, ProductName FROM Products WHERE ProductID = :id;
		""", {"id": id}).fetchone()

	if product is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	else:
		return{
			"id" : product["ProductID"],
			"name": product["ProductName"]
		}

@app.get("/employees", status_code=200)
async def employees(order: str = "EmployeeID", limit: Optional[int] = -1, offset: Optional[int] = 0):

	if order not in ["first_name", "last_name", "city", "EmployeeID"]:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
	elif order == "first_name":
		order = "FirstName"
	elif order == "last_name":
		order = "LastName"
	elif order == "city":
		order = "City"

	app.db_connection.row_factory = sqlite3.Row
	cursor = app.db_connection.cursor()
	employees = cursor.execute(f"""
		SELECT EmployeeID, LastName, FirstName, City FROM Employees
		ORDER BY {order} LIMIT {limit} OFFSET {offset};
		""").fetchall()

	return {"employees" : [{"id": x["EmployeeID"], "last_name": x["LastName"], "first_name": x["FirstName"], "city": x["City"] } for x in employees]}


@app.get("/products_extended", status_code=200)
async def products_extended():
	cursor = app.db_connection.cursor()

	cursor.row_factory = sqlite3.Row
	products_ex = cursor.execute("""
		SELECT Products.ProductID, Products.ProductName, Categories.CategoryName, Suppliers.CompanyName 
		FROM Products
		JOIN Categories ON Products.CategoryID = Categories.CategoryID
		JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID
		""").fetchall()

	ret = [{"id": x["ProductID"], "name": x["ProductName"], "category": x['CategoryName'], "supplier" : x["CompanyName"]} for x in products_ex]
	return {"products_extended": ret}


@app.get("/products/{id}/orders")
async def product_id_orders(id :int):
	cursor = app.db_connection.cursor()
	cursor.row_factory = sqlite3.Row
	orders = cursor.execute("""
		SELECT Orders.OrderID, Customers.CompanyName, "Order Details".Quantity,
		 (("Order Details".UnitPrice*"Order Details".Quantity) - ("Order Details".Discount*("Order Details".UnitPrice*"Order Details".Quantity))) AS total_price
		 FROM Orders
		 JOIN "Order Details" ON Orders.OrderID = "Order Details".OrderID
		 JOIN Customers ON Orders.CustomerID = Customers.CustomerID
		 WHERE "Order Details".ProductID =:id
		 ORDER BY Orders.OrderID

		""", {"id":id}).fetchall()

	if orders:
		ret = [{"id": x['OrderId'], "customer": x['CompanyName'], "quantity": x['Quantity'], "total_price": round(x['total_price'], 2)} for x in orders]
		return {"orders": ret}
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/categories", status_code=201)
async def post_categories(category:Category_Class):
	cursor = app.db_connection.cursor()
	cursor.row_factory = sqlite3.Row
	cursor.execute(f"""
		INSERT INTO Categories (CategoryName)
		VALUES ("{category.name}")
		""")
	app.db_connection.commit()
	return {
		"id" : cursor.lastrowid,
		"name" : category.name

	}


@app.put("/categories/{id}")
async def put_categories(id: int, category:Category_Class):
	cursor = app.db_connection.cursor()
	cursor.row_factory = sqlite3.Row
	category_id = cursor.execute(f"""
		SELECT CategoryID FROM Categories WHERE CategoryID = '{id}'
		""").fetchone()

	if category_id:
		cursor.execute(f"""
			UPDATE Categories
			SET CategoryName = '{category.name}'
			WHERE CategoryID = '{id}' 
			""")
		app.db_connection.commit()
		return {
			"id": id,
			"name": category.name
		}

	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.delete("/categories/{id}")
async def delete_categories(id: int):
	cursor = app.db_connection.cursor()
	cursor.row_factory = sqlite3.Row
	category_id = cursor.execute(f"""
		SELECT CategoryID FROM Categories WHERE CategoryID = '{id}'
		""").fetchone()

	if category_id:
		cursor.execute(f"""
			DELETE FROM Categories WHERE CategoryID = '{id}' 
			""")
		app.db_connection.commit()
		return {
			"deleted": 1
		}

	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

