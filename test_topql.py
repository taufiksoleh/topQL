"""
Unit tests for TopQL - Learning SQL Database
============================================
Comprehensive tests for all components: Tokenizer, Parser, Storage Engine, and Executor.
"""

import unittest
import tempfile
import shutil
import os
from topql import (
    Database, Tokenizer, Parser, StorageEngine, QueryExecutor,
    Token, TokenType, Table,
    CreateTableStatement, InsertStatement, SelectStatement,
    UpdateStatement, DeleteStatement, WhereClause
)


class TestTokenizer(unittest.TestCase):
    """Test the SQL tokenizer/lexer"""

    def test_simple_select(self):
        """Test tokenizing a simple SELECT statement"""
        sql = "SELECT * FROM users"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.SELECT)
        self.assertEqual(tokens[1].type, TokenType.ASTERISK)
        self.assertEqual(tokens[2].type, TokenType.FROM)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].value, "users")
        self.assertEqual(tokens[4].type, TokenType.EOF)

    def test_tokenize_create_table(self):
        """Test tokenizing CREATE TABLE statement"""
        sql = "CREATE TABLE users (id INT, name VARCHAR(50))"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.CREATE)
        self.assertEqual(tokens[1].type, TokenType.TABLE)
        self.assertEqual(tokens[2].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].type, TokenType.LPAREN)
        self.assertEqual(tokens[4].value, "id")
        self.assertEqual(tokens[5].type, TokenType.INT)
        self.assertEqual(tokens[6].type, TokenType.COMMA)

    def test_tokenize_string_literals(self):
        """Test tokenizing string literals"""
        sql = "INSERT INTO users VALUES ('Alice', 'Bob')"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        # Find string tokens
        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        self.assertEqual(len(string_tokens), 2)
        self.assertEqual(string_tokens[0].value, "Alice")
        self.assertEqual(string_tokens[1].value, "Bob")

    def test_tokenize_numbers(self):
        """Test tokenizing numbers"""
        sql = "SELECT * FROM users WHERE age > 25 AND id = 1"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        self.assertEqual(len(number_tokens), 2)
        self.assertEqual(number_tokens[0].value, 25)
        self.assertEqual(number_tokens[1].value, 1)

    def test_tokenize_operators(self):
        """Test tokenizing comparison operators"""
        sql = "WHERE a = 1 AND b != 2 AND c < 3 AND d > 4 AND e <= 5 AND f >= 6"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        operators = [t for t in tokens if t.type in (
            TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN,
            TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL
        )]
        self.assertEqual(len(operators), 6)

    def test_tokenize_booleans(self):
        """Test tokenizing boolean values"""
        sql = "INSERT INTO users VALUES (TRUE, FALSE)"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        bool_tokens = [t for t in tokens if t.type in (TokenType.TRUE, TokenType.FALSE)]
        self.assertEqual(len(bool_tokens), 2)
        self.assertEqual(bool_tokens[0].type, TokenType.TRUE)
        self.assertEqual(bool_tokens[1].type, TokenType.FALSE)


class TestParser(unittest.TestCase):
    """Test the SQL parser"""

    def test_parse_create_table(self):
        """Test parsing CREATE TABLE statement"""
        sql = "CREATE TABLE users (id INT, name VARCHAR(50), age INT)"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, CreateTableStatement)
        self.assertEqual(statement.table_name, "users")
        self.assertEqual(len(statement.columns), 3)
        self.assertEqual(statement.columns[0]["name"], "id")
        self.assertEqual(statement.columns[0]["type"], "INT")
        self.assertEqual(statement.columns[1]["name"], "name")
        self.assertEqual(statement.columns[1]["type"], "VARCHAR")

    def test_parse_insert(self):
        """Test parsing INSERT statement"""
        sql = "INSERT INTO users VALUES (1, 'Alice', 30)"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, InsertStatement)
        self.assertEqual(statement.table_name, "users")
        self.assertIsNone(statement.columns)
        self.assertEqual(len(statement.values), 3)
        self.assertEqual(statement.values[0], 1)
        self.assertEqual(statement.values[1], "Alice")
        self.assertEqual(statement.values[2], 30)

    def test_parse_insert_with_columns(self):
        """Test parsing INSERT with column specification"""
        sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, InsertStatement)
        self.assertEqual(statement.columns, ["id", "name"])
        self.assertEqual(statement.values, [1, "Alice"])

    def test_parse_select_all(self):
        """Test parsing SELECT * statement"""
        sql = "SELECT * FROM users"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, SelectStatement)
        self.assertEqual(statement.columns, ["*"])
        self.assertEqual(statement.table_name, "users")
        self.assertIsNone(statement.where_clause)

    def test_parse_select_columns(self):
        """Test parsing SELECT with specific columns"""
        sql = "SELECT id, name, age FROM users"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertEqual(statement.columns, ["id", "name", "age"])

    def test_parse_select_with_where(self):
        """Test parsing SELECT with WHERE clause"""
        sql = "SELECT * FROM users WHERE age > 25"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsNotNone(statement.where_clause)
        self.assertEqual(len(statement.where_clause.conditions), 1)
        self.assertEqual(statement.where_clause.conditions[0]["column"], "age")
        self.assertEqual(statement.where_clause.conditions[0]["operator"], ">")
        self.assertEqual(statement.where_clause.conditions[0]["value"], 25)

    def test_parse_select_with_multiple_where(self):
        """Test parsing SELECT with multiple WHERE conditions"""
        sql = "SELECT * FROM users WHERE age > 25 AND active = TRUE"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.where_clause.conditions), 2)
        self.assertEqual(statement.where_clause.logical_operators, ["AND"])

    def test_parse_select_with_order_by(self):
        """Test parsing SELECT with ORDER BY"""
        sql = "SELECT * FROM users ORDER BY age"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertEqual(statement.order_by, "age")

    def test_parse_select_with_limit(self):
        """Test parsing SELECT with LIMIT"""
        sql = "SELECT * FROM users LIMIT 10"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertEqual(statement.limit, 10)

    def test_parse_update(self):
        """Test parsing UPDATE statement"""
        sql = "UPDATE users SET age = 26 WHERE name = 'Bob'"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, UpdateStatement)
        self.assertEqual(statement.table_name, "users")
        self.assertEqual(statement.assignments, {"age": 26})
        self.assertIsNotNone(statement.where_clause)

    def test_parse_update_multiple_columns(self):
        """Test parsing UPDATE with multiple columns"""
        sql = "UPDATE users SET age = 26, active = TRUE"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.assignments), 2)
        self.assertEqual(statement.assignments["age"], 26)
        self.assertEqual(statement.assignments["active"], True)

    def test_parse_delete(self):
        """Test parsing DELETE statement"""
        sql = "DELETE FROM users WHERE age < 18"
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, DeleteStatement)
        self.assertEqual(statement.table_name, "users")
        self.assertIsNotNone(statement.where_clause)


class TestStorageEngine(unittest.TestCase):
    """Test the storage engine and table operations"""

    def setUp(self):
        """Set up test database"""
        self.storage = StorageEngine()
        self.storage.create_table("users", [
            {"name": "id", "type": "INT"},
            {"name": "name", "type": "VARCHAR"},
            {"name": "age", "type": "INT"}
        ])
        self.table = self.storage.get_table("users")

    def test_create_table(self):
        """Test creating a table"""
        self.assertIn("users", self.storage.tables)
        self.assertEqual(len(self.table.columns), 3)
        self.assertEqual(self.table.column_names, ["id", "name", "age"])

    def test_create_duplicate_table(self):
        """Test creating a table that already exists"""
        with self.assertRaises(ValueError):
            self.storage.create_table("users", [{"name": "id", "type": "INT"}])

    def test_get_nonexistent_table(self):
        """Test getting a table that doesn't exist"""
        with self.assertRaises(ValueError):
            self.storage.get_table("nonexistent")

    def test_insert_row(self):
        """Test inserting a row"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.assertEqual(len(self.table.rows), 1)
        self.assertEqual(self.table.rows[0]["name"], "Alice")

    def test_insert_missing_column(self):
        """Test inserting with missing column"""
        with self.assertRaises(ValueError):
            self.table.insert({"id": 1, "name": "Alice"})

    def test_insert_extra_column(self):
        """Test inserting with extra column"""
        with self.assertRaises(ValueError):
            self.table.insert({"id": 1, "name": "Alice", "age": 30, "extra": "value"})

    def test_select_all(self):
        """Test selecting all rows"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})

        rows = self.table.select(["*"])
        self.assertEqual(len(rows), 2)

    def test_select_specific_columns(self):
        """Test selecting specific columns"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})

        rows = self.table.select(["name", "age"])
        self.assertEqual(len(rows), 1)
        self.assertIn("name", rows[0])
        self.assertIn("age", rows[0])
        self.assertNotIn("id", rows[0])

    def test_select_with_where(self):
        """Test selecting with WHERE clause"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})
        self.table.insert({"id": 3, "name": "Charlie", "age": 35})

        where = WhereClause(
            conditions=[{"column": "age", "operator": ">", "value": 28}],
            logical_operators=[]
        )

        rows = self.table.select(["*"], where_clause=where)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["age"] > 28 for row in rows))

    def test_select_order_by(self):
        """Test selecting with ORDER BY"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})
        self.table.insert({"id": 3, "name": "Charlie", "age": 35})

        rows = self.table.select(["*"], order_by="age")
        self.assertEqual(rows[0]["age"], 25)
        self.assertEqual(rows[1]["age"], 30)
        self.assertEqual(rows[2]["age"], 35)

    def test_select_limit(self):
        """Test selecting with LIMIT"""
        for i in range(5):
            self.table.insert({"id": i, "name": f"User{i}", "age": 20 + i})

        rows = self.table.select(["*"], limit=3)
        self.assertEqual(len(rows), 3)

    def test_update_rows(self):
        """Test updating rows"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})

        where = WhereClause(
            conditions=[{"column": "name", "operator": "=", "value": "Bob"}],
            logical_operators=[]
        )

        count = self.table.update({"age": 26}, where)
        self.assertEqual(count, 1)
        self.assertEqual(self.table.rows[1]["age"], 26)

    def test_update_all_rows(self):
        """Test updating all rows without WHERE"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})

        count = self.table.update({"age": 99})
        self.assertEqual(count, 2)
        self.assertTrue(all(row["age"] == 99 for row in self.table.rows))

    def test_delete_rows(self):
        """Test deleting rows"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})
        self.table.insert({"id": 3, "name": "Charlie", "age": 35})

        where = WhereClause(
            conditions=[{"column": "age", "operator": "<", "value": 30}],
            logical_operators=[]
        )

        count = self.table.delete(where)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.table.rows), 2)

    def test_delete_all_rows(self):
        """Test deleting all rows"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})

        count = self.table.delete()
        self.assertEqual(count, 2)
        self.assertEqual(len(self.table.rows), 0)

    def test_where_clause_and_operator(self):
        """Test WHERE clause with AND operator"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})
        self.table.insert({"id": 3, "name": "Charlie", "age": 35})

        where = WhereClause(
            conditions=[
                {"column": "age", "operator": ">", "value": 25},
                {"column": "age", "operator": "<", "value": 35}
            ],
            logical_operators=["AND"]
        )

        rows = self.table.select(["*"], where_clause=where)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Alice")

    def test_where_clause_or_operator(self):
        """Test WHERE clause with OR operator"""
        self.table.insert({"id": 1, "name": "Alice", "age": 30})
        self.table.insert({"id": 2, "name": "Bob", "age": 25})
        self.table.insert({"id": 3, "name": "Charlie", "age": 35})

        where = WhereClause(
            conditions=[
                {"column": "age", "operator": "<", "value": 28},
                {"column": "age", "operator": ">", "value": 33}
            ],
            logical_operators=["OR"]
        )

        rows = self.table.select(["*"], where_clause=where)
        self.assertEqual(len(rows), 2)

    def test_list_tables(self):
        """Test listing all tables"""
        self.storage.create_table("products", [{"name": "id", "type": "INT"}])
        tables = self.storage.list_tables()
        self.assertIn("users", tables)
        self.assertIn("products", tables)

    def test_drop_table(self):
        """Test dropping a table"""
        self.storage.drop_table("users")
        self.assertNotIn("users", self.storage.tables)


class TestDatabase(unittest.TestCase):
    """Test the complete database interface"""

    def setUp(self):
        """Set up test database"""
        self.db = Database()

    def test_create_table_query(self):
        """Test CREATE TABLE via SQL"""
        result = self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.assertIn("message", result)
        self.assertIn("users", self.db.list_tables())

    def test_insert_query(self):
        """Test INSERT via SQL"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        result = self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.assertEqual(result["rows_affected"], 1)

    def test_select_query(self):
        """Test SELECT via SQL"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")

        result = self.db.execute("SELECT * FROM users")
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["rows"]), 2)

    def test_update_query(self):
        """Test UPDATE via SQL"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")

        result = self.db.execute("UPDATE users SET age = 31 WHERE name = 'Alice'")
        self.assertEqual(result["rows_affected"], 1)

        rows = self.db.execute("SELECT * FROM users")["rows"]
        self.assertEqual(rows[0]["age"], 31)

    def test_delete_query(self):
        """Test DELETE via SQL"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")

        result = self.db.execute("DELETE FROM users WHERE age < 30")
        self.assertEqual(result["rows_affected"], 1)

        rows = self.db.execute("SELECT * FROM users")["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Alice")

    def test_describe_table(self):
        """Test describing table structure"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50))")
        info = self.db.describe_table("users")

        self.assertEqual(info["name"], "users")
        self.assertEqual(len(info["columns"]), 2)
        self.assertEqual(info["row_count"], 0)

    def test_execute_many(self):
        """Test executing multiple queries"""
        queries = [
            "CREATE TABLE users (id INT, name VARCHAR(50))",
            "INSERT INTO users VALUES (1, 'Alice')",
            "INSERT INTO users VALUES (2, 'Bob')"
        ]

        results = self.db.execute_many(queries)
        self.assertEqual(len(results), 3)


class TestExampleQueries(unittest.TestCase):
    """Test the example queries from examples.py"""

    def setUp(self):
        """Set up test database"""
        self.db = Database()

    def test_example_1_create_and_insert(self):
        """Test Example 1: CREATE TABLE and INSERT"""
        # Create table
        result = self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT, active BOOLEAN)")
        self.assertIn("created successfully", result["message"])

        # Insert users
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30, TRUE)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25, TRUE)")
        self.db.execute("INSERT INTO users VALUES (3, 'Charlie', 35, FALSE)")

        # Verify
        result = self.db.execute("SELECT * FROM users")
        self.assertEqual(result["count"], 3)

    def test_example_2_select_basic(self):
        """Test Example 2: Basic SELECT queries"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")

        # Select all
        result = self.db.execute("SELECT * FROM users")
        self.assertEqual(result["count"], 2)

        # Select specific columns
        result = self.db.execute("SELECT name, age FROM users")
        self.assertEqual(len(result["rows"][0]), 2)
        self.assertIn("name", result["rows"][0])
        self.assertIn("age", result["rows"][0])
        self.assertNotIn("id", result["rows"][0])

    def test_example_3_select_where(self):
        """Test Example 3: SELECT with WHERE clause"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT, active BOOLEAN)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30, TRUE)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25, TRUE)")
        self.db.execute("INSERT INTO users VALUES (3, 'Charlie', 35, FALSE)")

        # Simple WHERE
        result = self.db.execute("SELECT * FROM users WHERE age > 28")
        self.assertEqual(result["count"], 2)

        # WHERE with equality
        result = self.db.execute("SELECT name, age FROM users WHERE active = TRUE")
        self.assertEqual(result["count"], 2)

        # Multiple conditions with AND
        result = self.db.execute("SELECT * FROM users WHERE age > 25 AND active = TRUE")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["rows"][0]["name"], "Alice")

        # Multiple conditions with OR
        result = self.db.execute("SELECT * FROM users WHERE age < 28 OR age > 33")
        self.assertEqual(result["count"], 2)

    def test_example_4_order_and_limit(self):
        """Test Example 4: ORDER BY and LIMIT"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
        self.db.execute("INSERT INTO users VALUES (3, 'Charlie', 35)")

        # Order by age
        result = self.db.execute("SELECT * FROM users ORDER BY age")
        self.assertEqual(result["rows"][0]["age"], 25)
        self.assertEqual(result["rows"][2]["age"], 35)

        # Limit results
        result = self.db.execute("SELECT * FROM users LIMIT 2")
        self.assertEqual(result["count"], 2)

        # Combine ORDER BY and LIMIT
        result = self.db.execute("SELECT name, age FROM users ORDER BY age LIMIT 2")
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["rows"][0]["age"], 25)

    def test_example_5_update(self):
        """Test Example 5: UPDATE statements"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")

        # Update with WHERE
        result = self.db.execute("UPDATE users SET age = 26 WHERE name = 'Bob'")
        self.assertEqual(result["rows_affected"], 1)

        # Verify the update
        result = self.db.execute("SELECT * FROM users WHERE name = 'Bob'")
        self.assertEqual(result["rows"][0]["age"], 26)

    def test_example_6_delete(self):
        """Test Example 6: DELETE statements"""
        self.db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")
        self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
        self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
        self.db.execute("INSERT INTO users VALUES (3, 'Charlie', 35)")

        # Delete with WHERE
        result = self.db.execute("DELETE FROM users WHERE age < 28")
        self.assertEqual(result["rows_affected"], 1)

        # Verify deletion
        result = self.db.execute("SELECT * FROM users")
        self.assertEqual(result["count"], 2)

    def test_example_7_ecommerce(self):
        """Test Example 7: E-Commerce database"""
        # Create products table
        self.db.execute("CREATE TABLE products (id INT, name VARCHAR(100), price INT, stock INT)")

        # Insert products
        self.db.execute("INSERT INTO products VALUES (1, 'Laptop', 999, 10)")
        self.db.execute("INSERT INTO products VALUES (2, 'Mouse', 25, 50)")
        self.db.execute("INSERT INTO products VALUES (3, 'Keyboard', 75, 30)")
        self.db.execute("INSERT INTO products VALUES (4, 'Monitor', 299, 15)")
        self.db.execute("INSERT INTO products VALUES (5, 'Webcam', 89, 20)")

        # Find expensive products
        result = self.db.execute("SELECT * FROM products WHERE price > 100")
        self.assertEqual(result["count"], 2)

        # Find low stock products
        result = self.db.execute("SELECT name, stock FROM products WHERE stock < 20")
        self.assertEqual(result["count"], 2)

        # Update stock
        self.db.execute("UPDATE products SET stock = 8 WHERE name = 'Laptop'")
        result = self.db.execute("SELECT stock FROM products WHERE name = 'Laptop'")
        self.assertEqual(result["rows"][0]["stock"], 8)

        # Get cheapest products
        result = self.db.execute("SELECT name, price FROM products ORDER BY price LIMIT 3")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["rows"][0]["name"], "Mouse")

    def test_complex_where_conditions(self):
        """Test complex WHERE conditions with mixed AND/OR"""
        self.db.execute("CREATE TABLE products (id INT, name VARCHAR(100), price INT, stock INT)")
        self.db.execute("INSERT INTO products VALUES (1, 'Laptop', 999, 10)")
        self.db.execute("INSERT INTO products VALUES (2, 'Mouse', 25, 50)")
        self.db.execute("INSERT INTO products VALUES (3, 'Keyboard', 75, 30)")

        # Test various operator combinations
        result = self.db.execute("SELECT * FROM products WHERE price >= 75")
        self.assertEqual(result["count"], 2)

        result = self.db.execute("SELECT * FROM products WHERE price <= 75")
        self.assertEqual(result["count"], 2)

        result = self.db.execute("SELECT * FROM products WHERE price != 999")
        self.assertEqual(result["count"], 2)

    def test_boolean_operations(self):
        """Test boolean values in queries"""
        self.db.execute("CREATE TABLE flags (id INT, active BOOLEAN, verified BOOLEAN)")
        self.db.execute("INSERT INTO flags VALUES (1, TRUE, FALSE)")
        self.db.execute("INSERT INTO flags VALUES (2, FALSE, TRUE)")
        self.db.execute("INSERT INTO flags VALUES (3, TRUE, TRUE)")

        result = self.db.execute("SELECT * FROM flags WHERE active = TRUE")
        self.assertEqual(result["count"], 2)

        result = self.db.execute("SELECT * FROM flags WHERE verified = FALSE")
        self.assertEqual(result["count"], 1)

    def test_edge_cases(self):
        """Test edge cases"""
        self.db.execute("CREATE TABLE test (id INT, value INT)")

        # Empty table select
        result = self.db.execute("SELECT * FROM test")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["rows"], [])

        # Insert and delete all
        self.db.execute("INSERT INTO test VALUES (1, 100)")
        self.db.execute("DELETE FROM test WHERE id = 1")
        result = self.db.execute("SELECT * FROM test")
        self.assertEqual(result["count"], 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test database"""
        self.db = Database()

    def test_select_nonexistent_table(self):
        """Test selecting from non-existent table"""
        with self.assertRaises(ValueError):
            self.db.execute("SELECT * FROM nonexistent")

    def test_insert_nonexistent_table(self):
        """Test inserting into non-existent table"""
        with self.assertRaises(ValueError):
            self.db.execute("INSERT INTO nonexistent VALUES (1, 'test')")

    def test_invalid_sql_syntax(self):
        """Test invalid SQL syntax"""
        with self.assertRaises(SyntaxError):
            self.db.execute("INVALID SQL QUERY")

    def test_column_count_mismatch(self):
        """Test column count mismatch in INSERT"""
        self.db.execute("CREATE TABLE test (id INT, name VARCHAR(50))")
        with self.assertRaises(ValueError):
            self.db.execute("INSERT INTO test VALUES (1)")

    def test_unknown_column_in_where(self):
        """Test unknown column in WHERE clause"""
        self.db.execute("CREATE TABLE test (id INT)")
        self.db.execute("INSERT INTO test VALUES (1)")

        # Should not raise error, just return no results
        result = self.db.execute("SELECT * FROM test WHERE unknown_column = 1")
        self.assertEqual(result["count"], 0)


class TestBinaryStorage(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="topql_bin_")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_save_and_autoload_select(self):
        db = Database(data_dir=self.tmpdir)
        db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT, active BOOLEAN)")
        db.execute("INSERT INTO users VALUES (1, 'Alice', 30, TRUE)")
        db.execute("INSERT INTO users VALUES (2, 'Bob', 25, TRUE)")
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "users.bin")))

        db2 = Database(data_dir=self.tmpdir)
        res = db2.execute("SELECT * FROM users WHERE age >= 30")
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["rows"][0]["name"], "Alice")

    def test_update_delete_persist(self):
        db = Database(data_dir=self.tmpdir)
        db.execute("CREATE TABLE test (id INT, v INT)")
        db.execute("INSERT INTO test VALUES (1, 10)")
        db.execute("INSERT INTO test VALUES (2, 20)")
        db.execute("INSERT INTO test VALUES (3, 30)")
        db.execute("UPDATE test SET v = 99 WHERE id = 2")
        db.execute("DELETE FROM test WHERE id = 1")

        db2 = Database(data_dir=self.tmpdir)
        res_all = db2.execute("SELECT * FROM test")
        self.assertEqual(res_all["count"], 2)
        res_99 = db2.execute("SELECT * FROM test WHERE v = 99")
        self.assertEqual(res_99["count"], 1)
        res_del = db2.execute("SELECT * FROM test WHERE id = 1")
        self.assertEqual(res_del["count"], 0)

    def test_enable_binary_storage_runtime(self):
        db = Database()
        db.execute("CREATE TABLE log (id INT, msg VARCHAR(50))")
        db.execute("INSERT INTO log VALUES (1, 'a')")
        db.enable_binary_storage(self.tmpdir)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "log.bin")))

        db2 = Database(data_dir=self.tmpdir)
        res = db2.execute("SELECT * FROM log WHERE id = 1")
        self.assertEqual(res["count"], 1)


if __name__ == "__main__":
    # Run all tests with verbose output
    unittest.main(verbosity=2)
