"""
SQLBridge MCP - A lightweight MCP server for Microsoft SQL Server.
Connects AI assistants to SQL Server databases via the Model Context Protocol.
https://github.com/Sobeih/sqlbridge-mcp
"""

import os
import re
from fastmcp import FastMCP
import pyodbc

mcp = FastMCP("SQLBridge MCP")

# Connection settings from environment
SERVER = os.getenv("SQLSERVER_INSTANCE", r"localhost\SQLEXPRESS")
DRIVER = "{ODBC Driver 17 for SQL Server}"
USERNAME = os.getenv("SQLSERVER_USER", "")
PASSWORD = os.getenv("SQLSERVER_PASSWORD", "")
ENCRYPT = os.getenv("SQLSERVER_ENCRYPT", "no")
TRUST_CERT = os.getenv("SQLSERVER_TRUST_CERT", "no")

# Safety mode: "readonly" (default), "readwrite", or "safe"
# readonly  = SELECT only, all writes blocked
# safe      = SELECT + INSERT/UPDATE allowed, DROP/ALTER/TRUNCATE/CREATE blocked
# readwrite = everything allowed (use with caution)
WRITE_MODE = os.getenv("SQLSERVER_WRITE_MODE", "readonly").lower()

# Dangerous operations that modify structure (blocked in readonly & safe modes)
DANGEROUS_OPS = re.compile(
    r"^\s*(DROP|ALTER|TRUNCATE|CREATE|EXEC|EXECUTE|GRANT|REVOKE|DENY|sp_)\b",
    re.IGNORECASE
)

# Write operations (blocked in readonly mode only)
WRITE_OPS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|MERGE)\b",
    re.IGNORECASE
)

def check_query_permission(query: str) -> str | None:
    """Check if query is allowed based on WRITE_MODE. Returns error message or None if allowed."""
    if WRITE_MODE == "readwrite":
        return None

    if DANGEROUS_OPS.search(query):
        return (
            f"BLOCKED: Dangerous operation detected. "
            f"Current mode: '{WRITE_MODE}'. "
            f"To allow this, set SQLSERVER_WRITE_MODE=readwrite in mcp.json."
        )

    if WRITE_MODE == "readonly" and WRITE_OPS.search(query):
        return (
            f"BLOCKED: Write operation detected. "
            f"Current mode: 'readonly'. "
            f"To allow INSERT/UPDATE/DELETE, set SQLSERVER_WRITE_MODE=safe in mcp.json. "
            f"To allow everything, set SQLSERVER_WRITE_MODE=readwrite."
        )

    return None

def get_connection(database: str = "master"):
    """Create SQL Server connection"""
    if USERNAME and PASSWORD:
        conn_str = (
            f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={database};"
            f"UID={USERNAME};PWD={PASSWORD};"
            f"Encrypt={ENCRYPT};TrustServerCertificate={TRUST_CERT};"
        )
    else:
        conn_str = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={database};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)


@mcp.tool()
def list_databases() -> str:
    """List all databases on SQL Server instance"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE state_desc = 'ONLINE' ORDER BY name")
        databases = [row[0] for row in cursor.fetchall()]
        conn.close()
        return f"Available databases:\n" + "\n".join(f"- {db}" for db in databases)
    except Exception as e:
        return f"Error listing databases: {str(e)}"


@mcp.tool()
def list_tables(database: str) -> str:
    """
    List all tables in specified database
    
    Args:
        database: Name of the database
    """
    try:
        conn = get_connection(database)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SCHEMA_NAME(schema_id) + '.' + name as full_name
            FROM sys.tables 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not tables:
            return f"No tables found in database '{database}'"
        return f"Tables in '{database}':\n" + "\n".join(f"- {t}" for t in tables)
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def get_table_schema(database: str, table_name: str) -> str:
    """
    Get column schema for a specific table
    
    Args:
        database: Name of the database
        table_name: Full table name (schema.table or just table)
    """
    try:
        conn = get_connection(database)
        cursor = conn.cursor()
        
        # Parse schema and table
        if '.' in table_name:
            schema, table = table_name.split('.', 1)
        else:
            schema = 'dbo'
            table = table_name
            
        cursor.execute("""
            SELECT 
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.is_nullable,
                c.is_identity
            FROM sys.columns c
            JOIN sys.types t ON c.user_type_id = t.user_type_id
            JOIN sys.tables tbl ON c.object_id = tbl.object_id
            JOIN sys.schemas s ON tbl.schema_id = s.schema_id
            WHERE s.name = ? AND tbl.name = ?
            ORDER BY c.column_id
        """, (schema, table))
        
        columns = []
        for row in cursor.fetchall():
            nullable = "NULL" if row[3] else "NOT NULL"
            identity = " IDENTITY" if row[4] else ""
            columns.append(f"  {row[0]}: {row[1]} {nullable}{identity}")
        
        conn.close()
        
        if not columns:
            return f"Table '{table_name}' not found in database '{database}'"
        return f"Schema for {schema}.{table}:\n" + "\n".join(columns)
    except Exception as e:
        return f"Error getting schema: {str(e)}"


@mcp.tool()
def execute_query(database: str, query: str, max_rows: int = 100) -> str:
    """
    Execute SQL query and return results
    
    Args:
        database: Name of the database
        query: SQL query to execute
        max_rows: Maximum number of rows to return (default 100)
    """
    try:
        # Safety check
        blocked = check_query_permission(query)
        if blocked:
            return blocked

        conn = get_connection(database)
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Handle SELECT queries
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(max_rows)
            
            if not rows:
                conn.close()
                return f"Query executed successfully. No rows returned."
            
            # Format results as table
            result = f"Columns: {', '.join(columns)}\n\n"
            for row in rows:
                result += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"
            
            total_rows = len(rows)
            if total_rows == max_rows:
                result += f"\n(Showing first {max_rows} rows - there may be more)"
            else:
                result += f"\n(Total: {total_rows} rows)"
            
            conn.commit()
            conn.close()
            return result
        else:
            # Handle INSERT/UPDATE/DELETE
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            return f"Query executed successfully. Rows affected: {affected}"
            
    except Exception as e:
        return f"Error executing query: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server without banner to keep STDIO clean for Cursor handshake
    mcp.run(show_banner=False)
