"""
TopQL - A Simple SQL Database for Learning
==========================================
This is a minimal SQL database implementation to understand how SQL works internally.

Components:
1. Tokenizer: Breaks SQL strings into tokens
2. Parser: Converts tokens into an Abstract Syntax Tree (AST)
3. Storage Engine: Manages tables and data in memory
4. Executor: Executes parsed queries against the storage engine
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from btree_index import BTreeIndex


# ============================================================================
# TOKENIZER - Breaks SQL text into meaningful tokens
# ============================================================================

class TokenType(Enum):
    """Types of tokens in SQL"""
    # Keywords
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    CREATE = "CREATE"
    TABLE = "TABLE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SET = "SET"
    ORDER = "ORDER"
    BY = "BY"
    LIMIT = "LIMIT"
    AND = "AND"
    OR = "OR"

    # Data types
    INT = "INT"
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"

    # Literals and identifiers
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    TRUE = "TRUE"
    FALSE = "FALSE"

    # Operators
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="

    # Punctuation
    COMMA = ","
    SEMICOLON = ";"
    LPAREN = "("
    RPAREN = ")"
    ASTERISK = "*"

    # Special
    EOF = "EOF"


@dataclass
class Token:
    """Represents a single token"""
    type: TokenType
    value: Any
    position: int


class Tokenizer:
    """Converts SQL text into tokens"""

    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
        'CREATE', 'TABLE', 'UPDATE', 'DELETE', 'SET', 'ORDER',
        'BY', 'LIMIT', 'AND', 'OR', 'INT', 'VARCHAR', 'BOOLEAN',
        'TRUE', 'FALSE'
    }

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        """Move to next character"""
        self.position += 1
        self.current_char = self.text[self.position] if self.position < len(self.text) else None

    def skip_whitespace(self):
        """Skip whitespace and newlines"""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def read_string(self) -> str:
        """Read a string literal enclosed in quotes"""
        quote_char = self.current_char
        self.advance()  # Skip opening quote
        result = ""
        while self.current_char and self.current_char != quote_char:
            result += self.current_char
            self.advance()
        if self.current_char == quote_char:
            self.advance()  # Skip closing quote
        return result

    def read_number(self) -> Union[int, float]:
        """Read a number"""
        result = ""
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return float(result) if '.' in result else int(result)

    def read_identifier(self) -> str:
        """Read an identifier or keyword"""
        result = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def tokenize(self) -> List[Token]:
        """Convert SQL text into list of tokens"""
        tokens = []

        while self.current_char:
            self.skip_whitespace()

            if not self.current_char:
                break

            pos = self.position

            # String literals
            if self.current_char in ('"', "'"):
                value = self.read_string()
                tokens.append(Token(TokenType.STRING, value, pos))

            # Numbers
            elif self.current_char.isdigit():
                value = self.read_number()
                tokens.append(Token(TokenType.NUMBER, value, pos))

            # Identifiers and keywords
            elif self.current_char.isalpha() or self.current_char == '_':
                value = self.read_identifier()
                upper_value = value.upper()

                if upper_value in self.KEYWORDS:
                    token_type = TokenType[upper_value]
                    tokens.append(Token(token_type, value, pos))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, value, pos))

            # Operators and punctuation
            elif self.current_char == '=':
                tokens.append(Token(TokenType.EQUALS, '=', pos))
                self.advance()
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.NOT_EQUALS, '!=', pos))
                    self.advance()
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.LESS_EQUAL, '<=', pos))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LESS_THAN, '<', pos))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.GREATER_EQUAL, '>=', pos))
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GREATER_THAN, '>', pos))
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', pos))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TokenType.SEMICOLON, ';', pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.ASTERISK, '*', pos))
                self.advance()
            else:
                raise SyntaxError(f"Unexpected character '{self.current_char}' at position {pos}")

        tokens.append(Token(TokenType.EOF, None, self.position))
        return tokens


# ============================================================================
# PARSER - Converts tokens into Abstract Syntax Tree (AST)
# ============================================================================

@dataclass
class CreateTableStatement:
    """AST node for CREATE TABLE"""
    table_name: str
    columns: List[Dict[str, str]]  # [{"name": "id", "type": "INT"}, ...]


@dataclass
class InsertStatement:
    """AST node for INSERT INTO"""
    table_name: str
    columns: Optional[List[str]]
    values: List[Any]


@dataclass
class SelectStatement:
    """AST node for SELECT"""
    columns: List[str]  # ["*"] or ["col1", "col2"]
    table_name: str
    where_clause: Optional['WhereClause']
    order_by: Optional[str]
    limit: Optional[int]


@dataclass
class UpdateStatement:
    """AST node for UPDATE"""
    table_name: str
    assignments: Dict[str, Any]  # {"col1": value1, "col2": value2}
    where_clause: Optional['WhereClause']


@dataclass
class DeleteStatement:
    """AST node for DELETE"""
    table_name: str
    where_clause: Optional['WhereClause']


@dataclass
class WhereClause:
    """AST node for WHERE conditions"""
    conditions: List[Dict[str, Any]]  # [{"column": "age", "operator": ">", "value": 18}]
    logical_operators: List[str]  # ["AND", "OR"]


class Parser:
    """Parses tokens into Abstract Syntax Tree"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, None, 0)

    def advance(self):
        """Move to next token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]

    def expect(self, token_type: TokenType) -> Token:
        """Expect current token to be of specific type and advance"""
        if self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type}")
        token = self.current_token
        self.advance()
        return token

    def parse(self):
        """Parse tokens into AST"""
        if self.current_token.type == TokenType.SELECT:
            return self.parse_select()
        elif self.current_token.type == TokenType.INSERT:
            return self.parse_insert()
        elif self.current_token.type == TokenType.CREATE:
            return self.parse_create_table()
        elif self.current_token.type == TokenType.UPDATE:
            return self.parse_update()
        elif self.current_token.type == TokenType.DELETE:
            return self.parse_delete()
        else:
            raise SyntaxError(f"Unexpected statement starting with {self.current_token.type}")

    def parse_create_table(self) -> CreateTableStatement:
        """Parse CREATE TABLE statement"""
        self.expect(TokenType.CREATE)
        self.expect(TokenType.TABLE)
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        columns = []
        while self.current_token.type != TokenType.RPAREN:
            col_name = self.expect(TokenType.IDENTIFIER).value

            # Get column type
            if self.current_token.type in (TokenType.INT, TokenType.VARCHAR, TokenType.BOOLEAN):
                col_type = self.current_token.value.upper()
                self.advance()
            else:
                raise SyntaxError(f"Expected data type, got {self.current_token.type}")

            # Handle VARCHAR(n)
            if col_type == "VARCHAR" and self.current_token.type == TokenType.LPAREN:
                self.advance()
                self.expect(TokenType.NUMBER)  # size
                self.expect(TokenType.RPAREN)

            columns.append({"name": col_name, "type": col_type})

            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RPAREN)
        return CreateTableStatement(table_name, columns)

    def parse_insert(self) -> InsertStatement:
        """Parse INSERT INTO statement"""
        self.expect(TokenType.INSERT)
        self.expect(TokenType.INTO)
        table_name = self.expect(TokenType.IDENTIFIER).value

        # Optional column list
        columns = None
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            columns = []
            while self.current_token.type != TokenType.RPAREN:
                columns.append(self.expect(TokenType.IDENTIFIER).value)
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RPAREN)

        self.expect(TokenType.VALUES)
        self.expect(TokenType.LPAREN)

        values = []
        while self.current_token.type != TokenType.RPAREN:
            if self.current_token.type == TokenType.NUMBER:
                values.append(self.current_token.value)
                self.advance()
            elif self.current_token.type == TokenType.STRING:
                values.append(self.current_token.value)
                self.advance()
            elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
                values.append(self.current_token.type == TokenType.TRUE)
                self.advance()
            else:
                raise SyntaxError(f"Unexpected value type: {self.current_token.type}")

            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RPAREN)
        return InsertStatement(table_name, columns, values)

    def parse_select(self) -> SelectStatement:
        """Parse SELECT statement"""
        self.expect(TokenType.SELECT)

        # Parse columns
        columns = []
        if self.current_token.type == TokenType.ASTERISK:
            columns.append("*")
            self.advance()
        else:
            while True:
                columns.append(self.expect(TokenType.IDENTIFIER).value)
                if self.current_token.type != TokenType.COMMA:
                    break
                self.advance()

        self.expect(TokenType.FROM)
        table_name = self.expect(TokenType.IDENTIFIER).value

        # Optional WHERE clause
        where_clause = None
        if self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where()

        # Optional ORDER BY
        order_by = None
        if self.current_token.type == TokenType.ORDER:
            self.advance()
            self.expect(TokenType.BY)
            order_by = self.expect(TokenType.IDENTIFIER).value

        # Optional LIMIT
        limit = None
        if self.current_token.type == TokenType.LIMIT:
            self.advance()
            limit = self.expect(TokenType.NUMBER).value

        return SelectStatement(columns, table_name, where_clause, order_by, limit)

    def parse_update(self) -> UpdateStatement:
        """Parse UPDATE statement"""
        self.expect(TokenType.UPDATE)
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SET)

        assignments = {}
        while True:
            col_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)

            if self.current_token.type == TokenType.NUMBER:
                value = self.current_token.value
                self.advance()
            elif self.current_token.type == TokenType.STRING:
                value = self.current_token.value
                self.advance()
            elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
                value = self.current_token.type == TokenType.TRUE
                self.advance()
            else:
                raise SyntaxError(f"Unexpected value type: {self.current_token.type}")

            assignments[col_name] = value

            if self.current_token.type != TokenType.COMMA:
                break
            self.advance()

        where_clause = None
        if self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where()

        return UpdateStatement(table_name, assignments, where_clause)

    def parse_delete(self) -> DeleteStatement:
        """Parse DELETE statement"""
        self.expect(TokenType.DELETE)
        self.expect(TokenType.FROM)
        table_name = self.expect(TokenType.IDENTIFIER).value

        where_clause = None
        if self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where()

        return DeleteStatement(table_name, where_clause)

    def parse_where(self) -> WhereClause:
        """Parse WHERE clause"""
        self.expect(TokenType.WHERE)

        conditions = []
        logical_operators = []

        while True:
            # Parse condition: column operator value
            column = self.expect(TokenType.IDENTIFIER).value

            # Get operator
            operator_map = {
                TokenType.EQUALS: '=',
                TokenType.NOT_EQUALS: '!=',
                TokenType.LESS_THAN: '<',
                TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=',
                TokenType.GREATER_EQUAL: '>='
            }

            if self.current_token.type not in operator_map:
                raise SyntaxError(f"Expected comparison operator, got {self.current_token.type}")

            operator = operator_map[self.current_token.type]
            self.advance()

            # Get value
            if self.current_token.type == TokenType.NUMBER:
                value = self.current_token.value
                self.advance()
            elif self.current_token.type == TokenType.STRING:
                value = self.current_token.value
                self.advance()
            elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
                value = self.current_token.type == TokenType.TRUE
                self.advance()
            else:
                raise SyntaxError(f"Unexpected value type: {self.current_token.type}")

            conditions.append({"column": column, "operator": operator, "value": value})

            # Check for AND/OR
            if self.current_token.type in (TokenType.AND, TokenType.OR):
                logical_operators.append(self.current_token.value.upper())
                self.advance()
            else:
                break

        return WhereClause(conditions, logical_operators)


# ============================================================================
# STORAGE ENGINE - Manages tables and data
# ============================================================================

class Table:
    """Represents a database table"""

    def __init__(self, name: str, columns: List[Dict[str, str]]):
        self.name = name
        self.columns = columns
        self.column_names = [col["name"] for col in columns]
        self.rows: List[Dict[str, Any]] = []
        self.indexes: Dict[str, BTreeIndex] = {col: BTreeIndex() for col in self.column_names}
        self._rows_by_id: Dict[int, Dict[str, Any]] = {}
        self._id_by_row: Dict[int, int] = {}
        self._next_row_id: int = 1

    def insert(self, values: Dict[str, Any]):
        row = values.copy()
        for col_name in self.column_names:
            if col_name not in row:
                raise ValueError(f"Missing value for column: {col_name}")
        for col_name in row:
            if col_name not in self.column_names:
                raise ValueError(f"Unknown column: {col_name}")
        row_id = self._next_row_id
        self._next_row_id += 1
        self._rows_by_id[row_id] = row
        self.rows.append(row)
        self._id_by_row[id(row)] = row_id
        for col_name in self.column_names:
            self.indexes[col_name].insert(row[col_name], row_id)

    def select(self, columns: List[str], where_clause: Optional[WhereClause] = None,
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        filtered_rows = self.rows
        if where_clause:
            filtered_rows = self._filter_rows(where_clause)

        # Order results
        if order_by:
            if order_by not in self.column_names:
                raise ValueError(f"Unknown column for ORDER BY: {order_by}")
            filtered_rows = sorted(filtered_rows, key=lambda row: row[order_by])

        # Apply limit
        if limit is not None:
            filtered_rows = filtered_rows[:limit]

        # Select specific columns
        if columns == ["*"]:
            return filtered_rows
        else:
            result = []
            for row in filtered_rows:
                selected_row = {col: row[col] for col in columns if col in row}
                result.append(selected_row)
            return result

    def update(self, assignments: Dict[str, Any], where_clause: Optional[WhereClause] = None) -> int:
        rows_to_update = self.rows if where_clause is None else self._filter_rows(where_clause)
        for row in rows_to_update:
            row_id = self._id_by_row.get(id(row))
            for col, value in assignments.items():
                if col in row:
                    old_value = row[col]
                    row[col] = value
                    if row_id is not None:
                        self.indexes[col].update(old_value, value, row_id)
        return len(rows_to_update)

    def delete(self, where_clause: Optional[WhereClause] = None) -> int:
        if where_clause is None:
            count = len(self.rows)
            for row in self.rows:
                row_id = self._id_by_row.get(id(row))
                if row_id is not None:
                    for col in self.column_names:
                        self.indexes[col].remove(row[col], row_id)
                    del self._rows_by_id[row_id]
                    del self._id_by_row[id(row)]
            self.rows = []
            return count
        rows_to_delete = self._filter_rows(where_clause)
        to_remove_ids = {id(r) for r in rows_to_delete}
        for row in rows_to_delete:
            row_id = self._id_by_row.get(id(row))
            if row_id is not None:
                for col in self.column_names:
                    self.indexes[col].remove(row[col], row_id)
                del self._rows_by_id[row_id]
                del self._id_by_row[id(row)]
        self.rows = [row for row in self.rows if id(row) not in to_remove_ids]
        return len(rows_to_delete)

    def _filter_rows_scan(self, where_clause: WhereClause) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for row in self.rows:
            condition_results = []
            for condition in where_clause.conditions:
                column = condition["column"]
                operator = condition["operator"]
                value = condition["value"]
                if column not in row:
                    condition_results.append(False)
                    continue
                row_value = row[column]
                if operator == '=':
                    condition_results.append(row_value == value)
                elif operator == '!=':
                    condition_results.append(row_value != value)
                elif operator == '<':
                    condition_results.append(row_value < value)
                elif operator == '>':
                    condition_results.append(row_value > value)
                elif operator == '<=':
                    condition_results.append(row_value <= value)
                elif operator == '>=':
                    condition_results.append(row_value >= value)
            if not condition_results:
                continue
            final_result = condition_results[0]
            for i, logical_op in enumerate(where_clause.logical_operators):
                if logical_op == 'AND':
                    final_result = final_result and condition_results[i + 1]
                elif logical_op == 'OR':
                    final_result = final_result or condition_results[i + 1]
            if final_result:
                result.append(row)
        return result

    def _filter_rows(self, where_clause: WhereClause) -> List[Dict[str, Any]]:
        if not where_clause.conditions:
            return []
        sets = []
        for condition in where_clause.conditions:
            column = condition["column"]
            operator = condition["operator"]
            value = condition["value"]
            idx = self.indexes.get(column)
            if idx is None:
                return self._filter_rows_scan(where_clause)
            sets.append(idx.query(operator, value))
        if not sets:
            return []
        combined = sets[0]
        for i, logical_op in enumerate(where_clause.logical_operators):
            next_set = sets[i + 1]
            if logical_op == 'AND':
                combined = combined.intersection(next_set)
            elif logical_op == 'OR':
                combined = combined.union(next_set)
        return [self._rows_by_id[s] for s in combined]


class StorageEngine:
    """Manages all tables in the database"""

    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def create_table(self, name: str, columns: List[Dict[str, str]]):
        """Create a new table"""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")

        self.tables[name] = Table(name, columns)

    def get_table(self, name: str) -> Table:
        """Get a table by name"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        return self.tables[name]

    def drop_table(self, name: str):
        """Drop a table"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        del self.tables[name]

    def list_tables(self) -> List[str]:
        """List all table names"""
        return list(self.tables.keys())


# ============================================================================
# EXECUTOR - Executes parsed SQL statements
# ============================================================================

class QueryExecutor:
    """Executes SQL statements against the storage engine"""

    def __init__(self, storage: StorageEngine):
        self.storage = storage

    def execute(self, statement):
        """Execute a parsed SQL statement"""
        if isinstance(statement, CreateTableStatement):
            return self._execute_create_table(statement)
        elif isinstance(statement, InsertStatement):
            return self._execute_insert(statement)
        elif isinstance(statement, SelectStatement):
            return self._execute_select(statement)
        elif isinstance(statement, UpdateStatement):
            return self._execute_update(statement)
        elif isinstance(statement, DeleteStatement):
            return self._execute_delete(statement)
        else:
            raise ValueError(f"Unknown statement type: {type(statement)}")

    def _execute_create_table(self, stmt: CreateTableStatement):
        """Execute CREATE TABLE"""
        self.storage.create_table(stmt.table_name, stmt.columns)
        return {"message": f"Table '{stmt.table_name}' created successfully"}

    def _execute_insert(self, stmt: InsertStatement):
        """Execute INSERT INTO"""
        table = self.storage.get_table(stmt.table_name)

        # Build row dictionary
        if stmt.columns:
            if len(stmt.columns) != len(stmt.values):
                raise ValueError("Column count doesn't match value count")
            row = dict(zip(stmt.columns, stmt.values))
        else:
            if len(table.column_names) != len(stmt.values):
                raise ValueError("Value count doesn't match table column count")
            row = dict(zip(table.column_names, stmt.values))

        table.insert(row)
        return {"message": "1 row inserted", "rows_affected": 1}

    def _execute_select(self, stmt: SelectStatement):
        """Execute SELECT"""
        table = self.storage.get_table(stmt.table_name)
        rows = table.select(stmt.columns, stmt.where_clause, stmt.order_by, stmt.limit)
        return {"rows": rows, "count": len(rows)}

    def _execute_update(self, stmt: UpdateStatement):
        """Execute UPDATE"""
        table = self.storage.get_table(stmt.table_name)
        count = table.update(stmt.assignments, stmt.where_clause)
        return {"message": f"{count} row(s) updated", "rows_affected": count}

    def _execute_delete(self, stmt: DeleteStatement):
        """Execute DELETE"""
        table = self.storage.get_table(stmt.table_name)
        count = table.delete(stmt.where_clause)
        return {"message": f"{count} row(s) deleted", "rows_affected": count}


# ============================================================================
# DATABASE - Main interface
# ============================================================================

class Database:
    """Main database interface - combines all components"""

    def __init__(self):
        self.storage = StorageEngine()
        self.executor = QueryExecutor(self.storage)

    def execute(self, sql: str):
        """Execute a SQL query and return results"""
        # Tokenize
        tokenizer = Tokenizer(sql)
        tokens = tokenizer.tokenize()

        # Parse
        parser = Parser(tokens)
        statement = parser.parse()

        # Execute
        result = self.executor.execute(statement)

        return result

    def execute_many(self, sql_list: List[str]):
        """Execute multiple SQL queries"""
        results = []
        for sql in sql_list:
            results.append(self.execute(sql))
        return results

    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        return self.storage.list_tables()

    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Describe a table's structure"""
        table = self.storage.get_table(table_name)
        return {
            "name": table.name,
            "columns": table.columns,
            "row_count": len(table.rows)
        }
