# SQLBridge MCP

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects AI assistants to Microsoft SQL Server databases.

Works with [Cursor](https://cursor.com/), [Claude Desktop](https://claude.ai/download), and any MCP-compatible client.

---

## Quick Start

### 1. Install Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Download & Install

```bash
git clone https://github.com/SobeihYahia/MCP-Server-SqlServer.git
cd MCP-Server-SqlServer
pip install -r requirements.txt
```

### 3. Add to Your AI Client

Pick your client below, copy the config, and replace the placeholders with your actual values.

<details>
<summary><b>Cursor</b></summary>

Edit the file `~/.cursor/mcp.json` (create it if it doesn't exist):

**Windows path:** `C:\Users\YOUR_USERNAME\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "my-sql-server": {
      "command": "python",
      "args": ["C:/path/to/MCP-Server-SqlServer/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "YOUR_SERVER_NAME\\YOUR_INSTANCE",
        "SQLSERVER_WRITE_MODE": "readonly"
      }
    }
  }
}
```

Restart Cursor after saving.

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Edit the file `claude_desktop_config.json`:

**Windows path:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS path:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-sql-server": {
      "command": "python",
      "args": ["C:/path/to/MCP-Server-SqlServer/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "YOUR_SERVER_NAME\\YOUR_INSTANCE",
        "SQLSERVER_WRITE_MODE": "readonly"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

</details>

### 4. Done!

Ask your AI assistant something like:

> "List all databases on my SQL Server"  
> "Show me the tables in the AdventureWorks database"  
> "Run a SELECT query on the Customers table"

---

## Features

- **Multi-Instance** — Connect to multiple SQL Server instances at once (local, remote, cloud).
- **Multi-Database** — Access any database on a connected instance by name.
- **Windows & SQL Auth** — Supports Trusted Connection and username/password.
- **Write Protection** — Three safety modes to control what the AI can do.
- **Single File** — One Python file, two dependencies. That's it.

## Available Tools

| Tool | Description |
|---|---|
| `list_databases` | List all online databases on the instance |
| `list_tables` | List all tables in a specific database |
| `get_table_schema` | Get column details for a specific table |
| `execute_query` | Execute SQL queries with safety controls |

---

## Configuration

### Authentication

**Windows Authentication** (local server, no password needed):

```json
"env": {
  "SQLSERVER_INSTANCE": "MYPC\\SQLEXPRESS"
}
```

**SQL Authentication** (cloud or remote server):

```json
"env": {
  "SQLSERVER_INSTANCE": "your-server.database.windows.net",
  "SQLSERVER_USER": "your_username",
  "SQLSERVER_PASSWORD": "your_password",
  "SQLSERVER_ENCRYPT": "yes",
  "SQLSERVER_TRUST_CERT": "yes"
}
```

### Multiple Instances

Add multiple entries under `mcpServers` — each one runs independently:

```json
{
  "mcpServers": {
    "local-db": {
      "command": "python",
      "args": ["C:/path/to/MCP-Server-SqlServer/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "MYPC\\SQLEXPRESS",
        "SQLSERVER_WRITE_MODE": "safe"
      }
    },
    "cloud-db": {
      "command": "python",
      "args": ["C:/path/to/MCP-Server-SqlServer/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "SQLSERVER_INSTANCE": "myserver.database.windows.net",
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

### All Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SQLSERVER_INSTANCE` | `localhost\SQLEXPRESS` | Server name or hostname |
| `SQLSERVER_USER` | — | Username (SQL Auth only) |
| `SQLSERVER_PASSWORD` | — | Password (SQL Auth only) |
| `SQLSERVER_ENCRYPT` | `no` | Encrypt connection (`yes` / `no`) |
| `SQLSERVER_TRUST_CERT` | `no` | Trust server certificate (`yes` / `no`) |
| `SQLSERVER_WRITE_MODE` | `readonly` | Safety mode (see below) |

---

## Write Protection

Control what SQL operations the AI is allowed to run:

| Mode | SELECT | INSERT / UPDATE / DELETE | DROP / ALTER / CREATE / TRUNCATE |
|---|---|---|---|
| **`readonly`** | Allowed | Blocked | Blocked |
| **`safe`** | Allowed | Allowed | Blocked |
| **`readwrite`** | Allowed | Allowed | Allowed |

Default is `readonly`. Blocked queries return a clear message explaining why and how to change the mode.

---

## Security

- Credentials in the config file are stored in **plaintext** — set proper file permissions.
- Always start with **`readonly`** mode and only escalate when needed.
- Parameterized queries are used internally to prevent SQL injection.
- Never use `readwrite` on production databases unless you understand the risks.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Sobeih Yahia** — [GitHub](https://github.com/SobeihYahia)
