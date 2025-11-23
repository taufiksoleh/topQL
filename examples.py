"""
TopQL Examples - Demonstrating SQL Query Execution
==================================================
This file contains examples showing how TopQL works internally.
"""

from topql import Database
import json


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(sql, result):
    """Pretty print SQL and its result"""
    print(f"\nSQL: {sql}")
    print("-" * 60)
    if "rows" in result:
        if result["rows"]:
            for row in result["rows"]:
                print(row)
        else:
            print("(no rows returned)")
        print(f"\nTotal rows: {result['count']}")
    else:
        print(result["message"])
    print()


def example_1_create_and_insert():
    """Example 1: Creating tables and inserting data"""
    print_section("Example 1: CREATE TABLE and INSERT")

    db = Database()

    # Create a users table
    sql = "CREATE TABLE users (id INT, name VARCHAR(50), age INT, active BOOLEAN)"
    result = db.execute(sql)
    print_result(sql, result)

    # Insert some users
    queries = [
        "INSERT INTO users VALUES (1, 'Alice', 30, TRUE)",
        "INSERT INTO users VALUES (2, 'Bob', 25, TRUE)",
        "INSERT INTO users VALUES (3, 'Charlie', 35, FALSE)",
        "INSERT INTO users VALUES (4, 'Diana', 28, TRUE)",
        "INSERT INTO users VALUES (5, 'Eve', 32, FALSE)"
    ]

    for sql in queries:
        result = db.execute(sql)
        print_result(sql, result)

    return db


def example_2_select_basic(db):
    """Example 2: Basic SELECT queries"""
    print_section("Example 2: Basic SELECT Queries")

    # Select all columns
    sql = "SELECT * FROM users"
    result = db.execute(sql)
    print_result(sql, result)

    # Select specific columns
    sql = "SELECT name, age FROM users"
    result = db.execute(sql)
    print_result(sql, result)


def example_3_select_where(db):
    """Example 3: SELECT with WHERE clause"""
    print_section("Example 3: SELECT with WHERE Clause")

    # Simple WHERE condition
    sql = "SELECT * FROM users WHERE age > 28"
    result = db.execute(sql)
    print_result(sql, result)

    # WHERE with equality
    sql = "SELECT name, age FROM users WHERE active = TRUE"
    result = db.execute(sql)
    print_result(sql, result)

    # Multiple conditions with AND
    sql = "SELECT * FROM users WHERE age > 25 AND active = TRUE"
    result = db.execute(sql)
    print_result(sql, result)

    # Multiple conditions with OR
    sql = "SELECT * FROM users WHERE age < 28 OR age > 33"
    result = db.execute(sql)
    print_result(sql, result)


def example_4_order_and_limit(db):
    """Example 4: ORDER BY and LIMIT"""
    print_section("Example 4: ORDER BY and LIMIT")

    # Order by age
    sql = "SELECT * FROM users ORDER BY age"
    result = db.execute(sql)
    print_result(sql, result)

    # Limit results
    sql = "SELECT * FROM users LIMIT 3"
    result = db.execute(sql)
    print_result(sql, result)

    # Combine ORDER BY and LIMIT
    sql = "SELECT name, age FROM users ORDER BY age LIMIT 2"
    result = db.execute(sql)
    print_result(sql, result)


def example_5_update(db):
    """Example 5: UPDATE statements"""
    print_section("Example 5: UPDATE Statements")

    # Update with WHERE
    sql = "UPDATE users SET age = 26 WHERE name = 'Bob'"
    result = db.execute(sql)
    print_result(sql, result)

    # Verify the update
    sql = "SELECT * FROM users WHERE name = 'Bob'"
    result = db.execute(sql)
    print_result(sql, result)

    # Update multiple rows
    sql = "UPDATE users SET active = TRUE WHERE age > 30"
    result = db.execute(sql)
    print_result(sql, result)

    # Show all users after update
    sql = "SELECT * FROM users"
    result = db.execute(sql)
    print_result(sql, result)


def example_6_delete(db):
    """Example 6: DELETE statements"""
    print_section("Example 6: DELETE Statements")

    # Show current state
    sql = "SELECT * FROM users"
    result = db.execute(sql)
    print_result(sql, result)

    # Delete with WHERE
    sql = "DELETE FROM users WHERE age < 28"
    result = db.execute(sql)
    print_result(sql, result)

    # Show remaining users
    sql = "SELECT * FROM users"
    result = db.execute(sql)
    print_result(sql, result)


def example_7_complex_scenario():
    """Example 7: More complex real-world scenario"""
    print_section("Example 7: E-Commerce Database")

    db = Database()

    # Create products table
    sql = "CREATE TABLE products (id INT, name VARCHAR(100), price INT, stock INT)"
    result = db.execute(sql)
    print_result(sql, result)

    # Insert products
    products_data = [
        "INSERT INTO products VALUES (1, 'Laptop', 999, 10)",
        "INSERT INTO products VALUES (2, 'Mouse', 25, 50)",
        "INSERT INTO products VALUES (3, 'Keyboard', 75, 30)",
        "INSERT INTO products VALUES (4, 'Monitor', 299, 15)",
        "INSERT INTO products VALUES (5, 'Webcam', 89, 20)"
    ]

    for sql in products_data:
        db.execute(sql)

    print("Inserted 5 products\n")

    # Find expensive products (price > 100)
    sql = "SELECT * FROM products WHERE price > 100"
    result = db.execute(sql)
    print_result(sql, result)

    # Find products with low stock
    sql = "SELECT name, stock FROM products WHERE stock < 20"
    result = db.execute(sql)
    print_result(sql, result)

    # Update stock after sale
    sql = "UPDATE products SET stock = 8 WHERE name = 'Laptop'"
    result = db.execute(sql)
    print_result(sql, result)

    # Get products sorted by price
    sql = "SELECT name, price FROM products ORDER BY price LIMIT 3"
    result = db.execute(sql)
    print_result(sql, result)


def example_8_understanding_internals():
    """Example 8: Understanding how SQL works internally"""
    print_section("Example 8: Understanding SQL Internals")

    print("""
This database helps you understand how SQL works internally:

1. TOKENIZER (Lexical Analysis)
   - Breaks SQL text into tokens (keywords, identifiers, operators, etc.)
   - Example: "SELECT * FROM users" becomes:
     [SELECT, *, FROM, IDENTIFIER('users')]

2. PARSER (Syntax Analysis)
   - Converts tokens into Abstract Syntax Tree (AST)
   - Validates SQL grammar
   - Creates structured representation of the query

3. STORAGE ENGINE
   - Manages tables and data in memory
   - Each table has columns (schema) and rows (data)
   - Provides operations: insert, select, update, delete

4. QUERY EXECUTOR
   - Takes AST and executes it against storage engine
   - Implements SQL logic (WHERE filtering, ORDER BY sorting, etc.)
   - Returns results

Let's trace through a query execution:
""")

    from topql import Tokenizer, Parser

    sql = "SELECT name FROM users WHERE age > 25"
    print(f"\nSQL: {sql}\n")

    # Step 1: Tokenization
    print("STEP 1 - Tokenization:")
    tokenizer = Tokenizer(sql)
    tokens = tokenizer.tokenize()
    for i, token in enumerate(tokens[:10]):  # Show first 10 tokens
        print(f"  Token {i}: {token.type.name:15} value={token.value}")

    # Step 2: Parsing
    print("\nSTEP 2 - Parsing:")
    parser = Parser(tokens)
    statement = parser.parse()
    print(f"  Statement Type: {type(statement).__name__}")
    print(f"  Columns: {statement.columns}")
    print(f"  Table: {statement.table_name}")
    if statement.where_clause:
        print(f"  WHERE Conditions: {statement.where_clause.conditions}")

    # Step 3 & 4: Storage and Execution
    print("\nSTEP 3 & 4 - Storage Engine & Execution:")
    db = Database()
    db.execute("CREATE TABLE users (name VARCHAR(50), age INT)")
    db.execute("INSERT INTO users VALUES ('Alice', 30)")
    db.execute("INSERT INTO users VALUES ('Bob', 20)")
    db.execute("INSERT INTO users VALUES ('Charlie', 35)")

    result = db.execute(sql)
    print(f"  Result: {result}")
    print("\n  Explanation: The executor filtered rows where age > 25")
    print("  and returned only the 'name' column from matching rows.")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 18 + "TopQL - Learning Database" + " " * 15 + "║")
    print("║" + " " * 12 + "Understanding SQL from the Inside" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")

    # Run all examples
    db = example_1_create_and_insert()
    example_2_select_basic(db)
    example_3_select_where(db)
    example_4_order_and_limit(db)
    example_5_update(db)
    example_6_delete(db)
    example_7_complex_scenario()
    example_8_understanding_internals()

    print_section("Summary")
    print("""
You've now seen how SQL works internally!

Key Concepts:
- CREATE TABLE: Defines table structure (schema)
- INSERT: Adds rows to a table
- SELECT: Retrieves data with optional filtering and sorting
- UPDATE: Modifies existing rows
- DELETE: Removes rows
- WHERE: Filters rows based on conditions
- ORDER BY: Sorts results
- LIMIT: Restricts number of results

Internal Process:
  SQL Text → Tokenizer → Parser → AST → Executor → Results
             ↓          ↓         ↓      ↓
           Tokens     Grammar   Tree   Storage
                              Check   Engine

Next Steps:
1. Read through topql.py to understand each component
2. Try modifying the code to add new features
3. Add support for JOIN, GROUP BY, or aggregate functions
4. Experiment with different query types

Happy Learning!
""")


if __name__ == "__main__":
    main()
