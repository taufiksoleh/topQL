# TopQL - A Learning SQL Database

**TopQL** is a minimal SQL database implementation built from scratch in Python to help you understand how SQL query languages work internally.

## Overview

This project implements a complete (albeit simple) SQL database engine including:
- **Tokenizer/Lexer**: Breaks SQL strings into tokens
- **Parser**: Converts tokens into an Abstract Syntax Tree (AST)
- **Storage Engine**: Manages tables and data in memory
- **Query Executor**: Executes parsed queries against the storage engine

## Features

### Supported SQL Statements

- ✅ `CREATE TABLE` - Define table schemas
- ✅ `INSERT INTO` - Add data to tables
- ✅ `SELECT` - Query data with filtering, sorting, and limits
- ✅ `UPDATE` - Modify existing rows
- ✅ `DELETE` - Remove rows from tables

### Supported SQL Features

- ✅ WHERE clauses with conditions (`=`, `!=`, `<`, `>`, `<=`, `>=`)
- ✅ Logical operators (`AND`, `OR`)
- ✅ ORDER BY for sorting results
- ✅ LIMIT for restricting result count
- ✅ Data types: `INT`, `VARCHAR`, `BOOLEAN`

## Quick Start

### Basic Usage

```python
from topql import Database

# Create a new database
db = Database()

# Create a table
db.execute("CREATE TABLE users (id INT, name VARCHAR(50), age INT)")

# Insert data
db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")

# Query data
result = db.execute("SELECT * FROM users WHERE age > 25")
print(result)
# Output: {'rows': [{'id': 1, 'name': 'Alice', 'age': 30}], 'count': 1}
```

### Run the Examples

```bash
python examples.py
```

This will run through comprehensive examples showing all features.

## How It Works

TopQL processes SQL queries in four main stages:

### 1. Tokenization (Lexical Analysis)

The tokenizer breaks SQL text into meaningful tokens:

```
"SELECT name FROM users WHERE age > 25"
    ↓
[SELECT, IDENTIFIER('name'), FROM, IDENTIFIER('users'), WHERE, IDENTIFIER('age'), >, NUMBER(25)]
```

**Code**: See `Tokenizer` class in `topql.py:85`

### 2. Parsing (Syntax Analysis)

The parser validates SQL grammar and builds an Abstract Syntax Tree:

```
Tokens → Parser → SelectStatement {
    columns: ['name'],
    table_name: 'users',
    where_clause: WhereClause {
        conditions: [{'column': 'age', 'operator': '>', 'value': 25}]
    }
}
```

**Code**: See `Parser` class in `topql.py:224`

### 3. Storage Engine

Manages tables and data in memory. Each table has:
- Schema (column definitions)
- Rows (actual data stored as dictionaries)

**Code**: See `Table` and `StorageEngine` classes in `topql.py:516`

### 4. Query Execution

The executor takes the AST and executes it against the storage engine:
- Filters rows based on WHERE conditions
- Sorts results with ORDER BY
- Limits results
- Returns formatted output

**Code**: See `QueryExecutor` class in `topql.py:623`

## SQL Examples

### CREATE TABLE
```sql
CREATE TABLE products (
    id INT,
    name VARCHAR(100),
    price INT,
    in_stock BOOLEAN
)
```

### INSERT
```sql
INSERT INTO products VALUES (1, 'Laptop', 999, TRUE)
INSERT INTO products (id, name, price) VALUES (2, 'Mouse', 25)
```

### SELECT
```sql
-- Select all
SELECT * FROM products

-- Select specific columns
SELECT name, price FROM products

-- With WHERE clause
SELECT * FROM products WHERE price > 100

-- Multiple conditions
SELECT * FROM products WHERE price > 50 AND in_stock = TRUE

-- With ORDER BY and LIMIT
SELECT name, price FROM products ORDER BY price LIMIT 5
```

### UPDATE
```sql
UPDATE products SET price = 899 WHERE name = 'Laptop'
UPDATE products SET in_stock = TRUE WHERE price < 100
```

### DELETE
```sql
DELETE FROM products WHERE price > 1000
DELETE FROM products WHERE in_stock = FALSE
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User SQL Query                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  TOKENIZER                                               │
│  • Breaks SQL into tokens (keywords, identifiers, etc.)  │
│  • Example: "SELECT" → Token(SELECT)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PARSER                                                  │
│  • Validates SQL grammar                                 │
│  • Builds Abstract Syntax Tree (AST)                     │
│  • Example: SelectStatement object                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  QUERY EXECUTOR                                          │
│  • Interprets AST                                        │
│  • Executes against Storage Engine                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  STORAGE ENGINE                                          │
│  • Manages tables in memory                              │
│  • Performs data operations (filter, sort, etc.)         │
│  • Returns results                                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Results Returned                       │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
topQL/
├── topql.py          # Main database implementation
│   ├── Tokenizer     # Lexical analysis
│   ├── Parser        # Syntax analysis
│   ├── Table         # Table data structure
│   ├── StorageEngine # Table management
│   ├── QueryExecutor # Query execution
│   └── Database      # Main interface
├── examples.py       # Comprehensive examples
└── README.md         # This file
```

## Learning Path

1. **Start with examples.py** - Run it to see TopQL in action
2. **Read the Tokenizer** - Understand how SQL text becomes tokens
3. **Study the Parser** - Learn how tokens become structured data
4. **Explore the Storage Engine** - See how data is stored and retrieved
5. **Examine the Executor** - Understand how queries are executed

## Extending TopQL

Here are some ideas to extend TopQL and deepen your understanding:

### Beginner
- Add support for `NULL` values
- Implement `COUNT(*)` aggregate function
- Add `LIKE` operator for string matching

### Intermediate
- Add `JOIN` support (INNER JOIN, LEFT JOIN)
- Implement `GROUP BY` and aggregate functions (`SUM`, `AVG`, `MAX`, `MIN`)
- Add indexes for faster lookups
- Persist data to disk

### Advanced
- Implement transactions (BEGIN, COMMIT, ROLLBACK)
- Add query optimization (query planner)
- Implement B-tree indexes
- Add support for subqueries

## Limitations

This is a learning database with intentional limitations:

- ❌ No disk persistence (all data in memory)
- ❌ No transactions or ACID guarantees
- ❌ No JOIN operations
- ❌ No indexes (full table scans only)
- ❌ No aggregate functions (COUNT, SUM, etc.)
- ❌ No NULL handling
- ❌ Limited data types
- ❌ No concurrent access support

These limitations make the code simpler to understand while still demonstrating the core concepts of SQL query processing.

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## License

This is an educational project. Feel free to use, modify, and learn from it!

## Contributing

This is a learning project, but suggestions and improvements are welcome! Some areas that could be enhanced:

- Better error messages
- More comprehensive tests
- Additional SQL features
- Performance optimizations
- Better documentation

## Resources

To learn more about database internals:

- **Books**:
  - "Database System Concepts" by Silberschatz, Korth, and Sudarshan
  - "Database Internals" by Alex Petrov

- **Online**:
  - [Let's Build a Simple Database](https://cstack.github.io/db_tutorial/)
  - [How does a relational database work](http://coding-geek.com/how-databases-work/)

---

Happy Learning! 🚀