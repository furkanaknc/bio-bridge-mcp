# Bio-Bridge

Bio-Bridge is a bioinformatics MCP server that exposes 27 tools over NCBI, RCSB PDB,
UniProt, KEGG, AlphaFold, and ClinVar.

## Architecture

The project now follows a code-first MCP layout:

- `src/server.py` is only the MCP bootstrap.
- `src/servers/<domain>/` contains thin tool wrappers.
- `src/shared/` contains shared instructions and lazy client initialization.
- `src/workflows/` contains reusable multi-step helpers.
- Existing API clients remain under the domain packages such as `src/ncbi/` and `src/rcsb/`.

This keeps wrappers small and filesystem-discoverable, and moves control flow and data
handling into code instead of the model context.

## Runtime Variants

- `lite`: uses the internal structure backend for mesh export
- `pymol`: adds an optional PyMOL backend for structure rendering, session export,
  and PyMOL-driven OBJ export

## Tool Groups

- Literature: `search_pubmed_papers`, `advanced_pubmed_search`, `get_pubmed_abstract`
- Gene expression: `search_geo_datasets`, `analyze_geo_series`, `classify_geo_samples`
- Genetics: `get_gene_info`, `search_genes`, `blast_sequence`, `fetch_sequence`
- Experimental structures: `pdb_search`, `pdb_get_summary`, `pdb_get_ligands`,
  `pdb_find_pockets`, `pdb_get_validation_report`, `pdb_search_by_uniprot`,
  `pdb_download_structure`
- Protein info: `get_uniprot_entry`, `search_uniprot_proteins`, `get_protein_go_terms`,
  `get_protein_pathways`
- Pathways: `search_kegg_pathway`, `get_kegg_pathway_info`, `get_kegg_pathway_genes`
- Predicted structures: `get_alphafold_structure`
- Clinical variants: `search_clinvar_variants`, `search_clinvar_by_gene`
- 3D structure export: `convert_structure_to_obj`, `convert_pdb_id_to_obj`,
  `analyze_structure`
- PyMOL visuals: `render_structure_image_tool`, `export_structure_session_tool`

## Important Rule

Use `pdb_*` tools for ligand and pocket analysis. AlphaFold entries are predicted
structures and do not provide ligand context.

## Run

### Local Execution

```bash
pip install -r requirements.txt
mcp dev src/server.py
```

Production:

```bash
python src/server.py
```

PyMOL-enabled environment:

```bash
pip install -r requirements-pymol.txt
python src/server.py
```

### Running with Docker

This MCP server is published on Docker Hub. You can run it directly without cloning/building the repository:

```bash
docker run -i --rm akncdocker/bio-bridge
```

If you prefer to build the image locally:
```bash
docker build -t akncdocker/bio-bridge .
```

---

## IDE & Client Integration

To use this MCP server in Claude Desktop, Cursor, or other compatible environments, use the configurations below.

### 1. Claude Desktop
Add this to your `claude_desktop_config.json` (Windows: `%APPDATA%\Claude\claude_desktop_config.json`, macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

#### Using Docker (Recommended - pulls automatically from Docker Hub)
```json
{
  "mcpServers": {
    "bio-bridge": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "NCBI_EMAIL=your.email@example.com",
        "-e", "NCBI_API_KEY=your_api_key_here",
        "akncdocker/bio-bridge"
      ]
    }
  }
}
```

#### Using Local Python Installation
```json
{
  "mcpServers": {
    "bio-bridge": {
      "command": "python",
      "args": [
        "C:/path/to/bio_bridge/src/server.py"
      ],
      "env": {
        "NCBI_EMAIL": "your.email@example.com",
        "NCBI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 2. Cursor
1. Open Cursor and navigate to **Settings** > **Features** > **MCP**.
2. Click **+ Add New MCP Server**.
3. Set the following values:
   - **Name**: `bio-bridge`
   - **Type**: `command`
   - **Command**: 
     - **For Docker:** `docker run -i --rm akncdocker/bio-bridge`
     - **For Local Python:** `python -u C:/path/to/bio_bridge/src/server.py`

### 3. Graphical Interfaces / Custom Extensions (e.g. Cline, Roo Code, VS Code Extensions)
If you are using a GUI-based MCP configuration panel where the launch command and its arguments are split:

1. **Name:** `bio-bridge`
2. **Type:** Choose **STDIO**
3. **Command to launch:** `docker`
4. **Arguments:** (Add each as a separate argument item/line)
   - `run`
   - `-i`
   - `--rm`
   - `akncdocker/bio-bridge`
5. **Environment variables:** (Optional)
   - **Key:** `NCBI_EMAIL` | **Value:** `your.email@example.com`
   - **Key:** `NCBI_API_KEY` | **Value:** `your_api_key_here`

---

## Test

```bash
python -m unittest discover -s tests -v
```

## Docker

Lite image:

```bash
docker build -t bio-bridge:lite .
```

PyMOL image:

```bash
docker build -f Dockerfile.pymol -t bio-bridge:pymol .
```

## Structure Backends

Structure export tools support:

- `backend="internal"` for fast built-in mesh generation
- `backend="pymol"` for PyMOL-driven structure views when the PyMOL runtime is installed

Example prompts:

```text
1CRN yapısını spheres temsilinde OBJ olarak dışa aktar.
```

```text
1CRN yapısını PyMOL backend ile surface OBJ olarak üret.
```

```text
1CRN için PyMOL backend kullanarak PNG render oluştur.
```

## Project Structure

```text
bio-bridge/
|-- src/
|   |-- server.py
|   |-- servers/
|   |-- shared/
|   |-- workflows/
|   |-- ncbi/
|   |-- rcsb/
|   |-- uniprot/
|   |-- kegg/
|   |-- alphafold/
|   `-- clinvar/
|-- tests/
|-- requirements.txt
`-- Dockerfile
```
