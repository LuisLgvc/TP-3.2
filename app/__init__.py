from flask import request, Flask, jsonify
from config import Config
from app.database import DatabaseConnection


def ejercicios_mysql():
    """Crea y configura la aplicación Flask junto con los endpoints y funciones necesarias"""

    app = Flask(__name__, static_folder=Config.STATIC_FOLDER,
                template_folder=Config.TEMPLATE_FOLDER)

    app.config.from_object(Config)

    @app.route('/product/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        try:
            query = """SELECT * FROM production.products AS PRP INNER JOIN production.brands AS PRD ON PRP.brand_id = PRD.brand_id INNER JOIN production.categories AS PRC ON PRP.category_id = PRC.category_id WHERE PRP.product_id = %s;"""
            params = product_id,
            result = DatabaseConnection.fetch_one(query, params)
            if result is not None:
                return {
                    "brand": {
                        "brand_id": result[6],
                        "brand_name": result[7]},
                    "category": {
                        "category_id": result[8],
                        "category_name": result[9]},
                    "list_price": result[5],
                    "model_year": result[4],
                    "product_id": result[0],
                    "product_name": result[1]
                }, 200
            else:
                return {"msg": "No se encontro el producto"}, 404
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return {'Error': error_message}, 400
        finally:
            DatabaseConnection.close_connection()

    @app.route('/products/<string:brand>/<string:categ>', methods=['GET'])
    def get_product_list(brand, categ):
        try:
            query = """SELECT PRP.product_id, PRP.product_name, PRP.model_year, PRP.list_price, PRP.brand_id, PRD.brand_name, PRP.category_id, PRC.category_name FROM production.products AS PRP 
            INNER JOIN production.brands AS PRD ON PRP.brand_id = PRD.brand_id 
            INNER JOIN production.categories AS PRC ON PRP.category_id = PRC.category_id 
            WHERE PRD.brand_name LIKE %s AND PRC.category_name LIKE %s;"""
            lista = []
            params = ("%" + brand + "%", "%" + categ + "%",)
            results = DatabaseConnection.fetch_all(query, params)
            if len(results) > 0:
                for result in results:
                    lista.append({
                        "brand": {
                            "brand_id": result[4],
                            "brand_name": result[5]},
                        "category": {
                            "category_id": result[6],
                            "category_name": result[7]},
                        "list_price": result[3],
                        "model_year": result[2],
                        "product_id": result[0],
                        "product_name": result[1]
                    })
                return {"products": lista, "total": len(lista)}, 200   
            else:
                return {"Mensaje": "No se encontraron coincidencias"}, 404
        except Exception as e:
            error_message = str(e)
            return {'Error': error_message}, 400
        finally:
            DatabaseConnection.close_connection()

    @app.route('/addproduct', methods=['POST'])
    def add_product():
        try:
            query = """INSERT INTO production.products (product_name, brand_id, category_id, model_year, list_price)
            VALUES (%s, %s, %s, %s, %s);"""

            product_name = request.args.get('product_name', '')
            brand_id = int(request.args.get('brand_id', ''))
            category_id = int(request.args.get('category_id', ''))
            model_year = int(request.args.get('model_year', ''))
            list_price = float(request.args.get('list_price', ''))

            params = (product_name, brand_id, category_id, model_year, list_price)
            DatabaseConnection.execute_query(query, params)

            return '{ }', 201
        except:
            return {'Error': 'Ha ocurrido un error'}, 400
        finally:
            DatabaseConnection.close_connection()

    @app.route('/updproduct/<int:product_id>', methods=['PUT'])
    def update_product(product_id):
        try:
            update_values = []

            product_name = request.args.get('product_name', '')
            brand_id = request.args.get('brand_id', '')
            category_id = request.args.get('category_id', '')
            model_year = request.args.get('model_year', '')
            list_price = request.args.get('list_price', '')

            if product_name:
                update_values.append(f"product_name = '{product_name}'")
            if brand_id:
                update_values.append(f"brand_id = {int(brand_id)}")
            if category_id:
                update_values.append(f"category_id = {int(category_id)}")
            if model_year:
                update_values.append(f"model_year = {int(model_year)}")
            if list_price:
                update_values.append(f"list_price = {float(list_price)}")
            if len(update_values) == 0:
                return jsonify({"message": "No se proporcionaron datos para actualizar"}), 400

            query = "UPDATE production.products SET " + ", ".join(update_values) + " WHERE product_id = %s"

            params = product_id,

            DatabaseConnection.execute_query(query, params)
            
            return '{ }', 200
        except Exception as e:
            return {"error": str(e)}, 400
        finally:
            DatabaseConnection.close_connection()

    @app.route('/delproduct/<int:product_id>')
    def delete_product(product_id):
        try:
            query = "DELETE FROM production.products WHERE product_id = %s;"

            params = product_id,
        
            DatabaseConnection.execute_query(query, params)

            return '{ }', 204
        except Exception as e:
            return {'Error': str(e)}, 400
        finally:
            DatabaseConnection.close_connection()

    return app
