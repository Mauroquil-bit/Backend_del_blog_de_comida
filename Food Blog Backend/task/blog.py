import argparse
import sqlite3
import sys

if len(sys.argv) > 1:
    database_name = sys.argv[1]
else:
    print("Por favor, proporciona el nombre de la base de datos como argumento.")
    sys.exit(1)

# Conexión a la base de datos SQLite
conn = sqlite3.connect(database_name)
cursor = conn.cursor()


def add_recipes(cursor):
    meals_dict = {"1": "breakfast", "2": "brunch", "3": "lunch", "4": "supper"}

    while True:
        recipe_name = input("Recipe name: ")
        if recipe_name == "":
            break
        recipe_description = input("Recipe description: ")
        cursor.execute('INSERT INTO recipes (recipe_name, recipe_description) VALUES (?, ?)',
                       (recipe_name, recipe_description))
        conn.commit()

        recipe_id = cursor.lastrowid

        print("1) breakfast  2) brunch  3) lunch  4) supper")
        recipe_meal = input("Enter proposed meals separated by a space: ")

        for meal_number in recipe_meal.split():
            meal_name = meals_dict.get(meal_number)
            if meal_name:
                print(f"Buscando meal_id para: {meal_name}")
                cursor.execute('SELECT meal_id FROM meals WHERE meal_name = ?', (meal_name,))
                result = cursor.fetchone()
                if result:
                    meal_id = result[0]
                    print(f"Encontrado meal_id {meal_id} para {meal_name}")
                    cursor.execute('INSERT INTO serve (recipe_id, meal_id) VALUES (?, ?)', (recipe_id, meal_id))
                else:
                    print(f"La comida '{meal_name}' no se encontró en la base de datos.")
            else:
                print(f"El número de comida '{meal_number}' no es válido.")
        conn.commit()



        # Procesar los ingredientes
        while True:
            ingredient_input = input("Input quantity of ingredient <press enter to stop>: ")
            if ingredient_input == "":
                break

            parts = ingredient_input.split()
            if len(parts) < 3:
                print("Formato incorrecto. Asegúrate de incluir cantidad, medida y nombre del ingrediente.")
                continue

            quantity = parts[0]
            measure = parts[1]
            ingredient_name = ' '.join(parts[2:])

            print(f"Procesando ingrediente: {quantity} {measure} {ingredient_name}")

            cursor.execute('SELECT ingredient_id FROM ingredients WHERE ingredient_name = ?', (ingredient_name,))
            result = cursor.fetchone()
            if result:
                ingredient_id = result[0]
                print(f"Encontrado ingredient_id {ingredient_id} para {ingredient_name}")

                cursor.execute('SELECT measure_id FROM measures WHERE measure_name = ?', (measure,))
                result = cursor.fetchone()
                if result:
                    measure_id = result[0]
                    print(f"Encontrado measure_id {measure_id} para {measure}")

                    cursor.execute(
                        'INSERT INTO quantity (quantity, measure_id, ingredient_id, recipe_id) VALUES (?, ?, ?, ?)',
                        (quantity, measure_id, ingredient_id, recipe_id))
                    print(f"Insertando {quantity} {measure} {ingredient_name} en quantity")
                    conn.commit()


                else:
                    print(f"La medida '{measure}' no se encontró en la base de datos.")
            else:
                print(f"El ingrediente '{ingredient_name}' no se encontró en la base de datos.")



def search_recipes(cursor, ingredients, meals):
    # Lógica para buscar recetas
    ingredients = ingredients.split(",")
    meals = meals.split(",")
    recipes = []
    for meal in meals:
        cursor.execute('SELECT recipe_id FROM serve WHERE meal_id = ?', (meal,))
        recipes.append(set(cursor.fetchall()))
    recipes = set.intersection(*recipes)
    for ingredient in ingredients:
        cursor.execute('SELECT recipe_id FROM quantity WHERE ingredient_id = ?', (ingredient,))
        recipes = recipes.intersection(set(cursor.fetchall()))
    if recipes:
        cursor.execute('SELECT recipe_name FROM recipes WHERE recipe_id IN ({})'.format(
            ', '.join([str(recipe[0]) for recipe in recipes])))
        print("Recipes selected for you: {}".format(", ".join([recipe[0] for recipe in cursor.fetchall()])))
    else:
        print("There are no such recipes in the database.")


def main(database_name, ingredients, meals):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()

    # Crear las tablas según el esquema proporcionado
    cursor.execute('''CREATE TABLE IF NOT EXISTS measures (
                    measure_id INTEGER PRIMARY KEY,
                    measure_name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                    ingredient_id INTEGER PRIMARY KEY,
                    ingredient_name TEXT NOT NULL UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS meals (
                    meal_id INTEGER PRIMARY KEY,
                    meal_name TEXT NOT NULL UNIQUE)''')

    # Crear la nueva tabla recipes según el esquema proporcionado
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                    recipe_id INTEGER PRIMARY KEY,
                    recipe_name TEXT NOT NULL,
                    recipe_description TEXT)''')

    # Crear la tabla 'serve'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS serve (
        serve_id INTEGER PRIMARY KEY,
        recipe_id INTEGER NOT NULL,
        meal_id INTEGER NOT NULL,
        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
        FOREIGN KEY(meal_id) REFERENCES meals(meal_id)
    )
    ''')
    conn.commit()  # Confirmar la creación de la tabla 'serve'

    # Crear la tabla 'quantity'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quantity (
        quantity_id INTEGER PRIMARY KEY,
        quantity INTEGER NOT NULL,
        measure_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
        FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id),
        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)
    )
    ''')
    conn.commit()  # Confirmar la creación de la tabla 'quantity'

    # Datos para poblar las tablas
    data = {
        "meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
    }

    # Poblar las tablas
    for table, items in data.items():
        cursor.executemany(f'INSERT INTO {table} ({table[:-1]}_name) VALUES (?) ON CONFLICT DO NOTHING',
                           [(item,) for item in items])

    conn.commit()

    if ingredients and meals:
        search_recipes(cursor, ingredients, meals)
    else:
        add_recipes(cursor)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Food Blog Backend")
    parser.add_argument("database_name", help="Name of the database")
    parser.add_argument("--ingredients", help="List of ingredients", default="")
    parser.add_argument("--meals", help="List of meals", default="")
    args = parser.parse_args()

    main(args.database_name, args.ingredients, args.meals)
