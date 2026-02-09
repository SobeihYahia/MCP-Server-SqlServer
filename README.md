# SQLBridge MCP

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects AI assistants to Microsoft SQL Server databases. Built for [Cursor](https://cursor.com/) and any MCP-compatible client.

## Features

- **Multi-Instance Support** — Connect to multiple SQL Server instances (local, remote, or cloud) simultaneously.
- **Multi-Database Access** — Query any database on a connected instance by name.
- **Windows & SQL Authentication** — Supports both Trusted Connection and username/password authentication.
- **Write Protection** — Three safety modes (`readonly`, `safe`, `readwrite`) to control what operations the AI can execute.
- **Zero Configuration** — Single Python file, two dependencies, works out of the box.

## Tools

| Tool | Description |
|---|---|
| `list_databases` | List all online databases on the instance |
| `list_tables` | List all tables in a specific database |
| `get_table_schema` | Get column details for a specific table |
| `execute_query` | Execute SQL queries with safety controls |

## Requirements

- Python 3.10+
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Installation

```bash
git clone https://github.com/SobeihYahia/MCP-Server-SqlServer.git
cd MCP-Server-SqlServer
pip install -r requirements.txt
```

## Setup (Cursor)

Add to your **global** Cursor MCP config at `~/.cursor/mcp.json`:

### Local Instance (Windows Authentication)

```json
{
  "mcpServers": {
    "sqlserver-local": {
      "command": "python",
      "args": ["C:/path/to/sqlbridge-mcp/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "MYPC\\SQLEXPRESS",
        "SQLSERVER_WRITE_MODE": "readonly"
      }
    }
  }
}
```

### Cloud / Remote Instance (SQL Authentication)

```json
{
  "mcpServers": {
    "sqlserver-cloud": {
      "command": "python",
      "args": ["C:/path/to/sqlbridge-mcp/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "your-server.database.windows.net",
        "SQLSERVER_USER": "your_username",
        "SQLSERVER_PASSWORD": "your_password",
        "SQLSERVER_ENCRYPT": "yes",
        "SQLSERVER_TRUST_CERT": "yes",
        "SQLSERVER_WRITE_MODE": "readonly"
      }
    }
  }
}
```

### Multiple Instances

Add multiple entries under `mcpServers` — each runs its own server process with independent configuration:

```json
{
  "mcpServers": {
    "local-db": {
      "command": "python",
      "args": ["C:/path/to/sqlbridge-mcp/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "MYPC\\SQLEXPRESS",
        "SQLSERVER_WRITE_MODE": "safe"
      }
    },
    "prod-db": {
      "command": "python",
      "args": ["C:/path/to/sqlbridge-mcp/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "prod-server.database.windows.net",
        "SQLSERVER_USER": "admin",
        "SQLSERVER_PASSWORD": "secret",
        "SQLSERVER_ENCRYPT": "yes",
        "SQLSERVER_TRUST_CERT": "yes",
        "SQLSERVER_WRITE_MODE": "readonly"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SQLSERVER_INSTANCE` | No | `SOBEIH\SQLSERVER2022` | SQL Server instance name or hostname |
| `SQLSERVER_USER` | No | — | Username for SQL Authentication |
| `SQLSERVER_PASSWORD` | No | — | Password for SQL Authentication |
| `SQLSERVER_ENCRYPT` | No | `no` | Enable encrypted connection (`yes`/`no`) |
| `SQLSERVER_TRUST_CERT` | No | `no` | Trust server certificate (`yes`/`no`) |
| `SQLSERVER_WRITE_MODE` | No | `readonly` | Safety mode (see below) |

## Write Protection Modes

Control what SQL operations the AI assistant is allowed to execute:

| Mode | SELECT | INSERT / UPDATE / DELETE | DROP / ALTER / CREATE / TRUNCATE |
|---|---|---|---|
| `readonly` | Allowed | **Blocked** | **Blocked** |
| `safe` | Allowed | Allowed | **Blocked** |
| `readwrite` | Allowed | Allowed | Allowed |

Default is `readonly`. Change per-instance via `SQLSERVER_WRITE_MODE` in your `mcp.json`.

When a query is blocked, the server returns a clear message explaining why and how to change the mode.

## Security Notes

- **Credentials in `mcp.json`** are stored in plaintext. Ensure appropriate file permissions on your machine.
- **Default to `readonly`** — only escalate write permissions when intentionally needed.
- **Parameterized queries** are used internally to prevent SQL injection in schema lookups.
- **Never expose `readwrite` mode** on production databases unless you fully understand the risks.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Sobeih Yahia** — [GitHub](https://github.com/SobeihYahia)
