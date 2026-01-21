# Bio-Bridge

Bio-Bridge is an MCP (Model Context Protocol) server that bridges Large Language Models (LLMs) with the NCBI GEO (Gene Expression Omnibus) database.

Its primary purpose is to distinguish between **Treated** and **Control** samples in raw metadata using heuristic analysis.

## Features

- Fetches sample metadata from NCBI GEO using `Bio.Entrez`.
- Heuristically classifies samples as "Treated" or "Control".
- Extracts dosage information (e.g., "50 mg/kg") using Regex.
- Exposes an MCP tool called `analyze_sample`.

## Installation

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Duplicate the example env file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit `.env`:**
    Open the `.env` file and set `NCBI_EMAIL` to your actual NCBI email address.
    ```text
    NCBI_EMAIL=your.email@example.com
    ```
    _Note: NCBI requires this to act as a contact if there are issues with your API usage._

### Alternative: Configuration via MCP Client (JSON)

If you prefer not to use a `.env` file, you can pass the email directly in your MCP client configuration (e.g., `claude_desktop_config.json`).

**For Local Python:**

```json
"bio-bridge": {
  "command": "path/to/venv/python",
  "args": ["src/server.py"],
  "env": {
    "NCBI_EMAIL": "your.email@example.com"
  }
}
```

**For Docker:**
Pass it in the `args` list:

```json
"args": ["run", "-i", "--rm", "-e", "NCBI_EMAIL=your.email@example.com", "bio-bridge"]
```

## Usage

### Running the MCP Server

You can run the server using the `mcp` CLI (installed via `mcp[cli]`):

```bash
mcp dev src/server.py
```

### Running with Docker (Recommended for Distribution)

If you want to run this without managing Python environments, you can use Docker.

1.  **Build the Image:**

    ```bash
    docker build -t bio-bridge .
    ```
2.  **Run with MCP Client:**
    Configure your MCP client (like Claude Desktop) to run the docker container.

    **Command:** `docker`
    **Args:**

    ```json
    [
      "run",
      "-i",
      "--rm",
      "-e",
      "NCBI_EMAIL=your.email@example.com",
      "bio-bridge"
    ]
    ```

    _(Note: The `-i` flag is critical for MCP communication over Stdio.)_

### Testing Docker Manually

You can test if the image works by piping a command into it (advanced usage), or just checking if it starts without error (it will wait for input):

```bash
docker run -i --rm -e NCBI_EMAIL=test@test.com bio-bridge
```

_(It will appear to hang as it waits for MCP JSON-RPC messages - this is normal)._

### Using the Tool

Once the server is running and connected to your MCP client (like Claude Desktop or an IDE), you can ask:

> "Analyze the GEO sample GSM123456"

The tool `analyze_sample` will be called, and it will return a structured summary of the sample.

## Project Structure

- `src/parsing_logic.py`: Core logic for fetching and classifying data.
- `src/server.py`: Definition of the MCP server and tools.
