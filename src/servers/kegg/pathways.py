from shared.clients import get_kegg_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_kegg_tools(mcp):
    @mcp.tool(title="Search KEGG pathways", annotations=READ_ONLY_OPEN_WORLD)
    def search_kegg_pathway(query: str, organism: str = "hsa") -> str:
        """Search for KEGG pathways by keyword."""
        kegg_client = get_kegg_client()
        if not kegg_client:
            return "Error: KEGG Client is not initialized."

        try:
            results = kegg_client.search_pathway(query, organism)
            if not results:
                return f"No pathways found for '{query}'"
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"

            output = [f"### KEGG Pathway Search Results for '{query}'"]
            for pathway in results:
                output.append(f"- **{pathway['id']}**: {pathway['name']}")
            output.append("")
            output.append(
                "*Use `get_kegg_pathway_info` for pathway details or "
                "`get_kegg_pathway_genes` for the gene list.*"
            )
            return "\n".join(output)
        except Exception as exc:
            return f"Error searching pathways: {exc}"

    @mcp.tool(title="Get KEGG pathway details", annotations=READ_ONLY_OPEN_WORLD)
    def get_kegg_pathway_info(pathway_id: str) -> str:
        """Get details of a specific KEGG pathway."""
        kegg_client = get_kegg_client()
        if not kegg_client:
            return "Error: KEGG Client is not initialized."

        try:
            result = kegg_client.get_pathway_info(pathway_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### KEGG Pathway: {result['id']}"]
            output.append(f"**Name:** {result.get('name', 'N/A')}")
            if result.get("description"):
                output.append(f"**Description:** {result['description']}")
            output.append("---")

            genes = result.get("genes", [])
            if genes:
                output.append(f"**Genes ({len(genes)} shown):**")
                for gene in genes[:15]:
                    output.append(
                        f"- {gene.get('id', 'N/A')} ({gene.get('symbol', '')}): "
                        f"{gene.get('description', '')[:50]}"
                    )

            return "\n".join(output)
        except Exception as exc:
            return f"Error getting pathway info: {exc}"

    @mcp.tool(title="Get KEGG pathway genes", annotations=READ_ONLY_OPEN_WORLD)
    def get_kegg_pathway_genes(pathway_id: str) -> str:
        """Get the list of genes in a KEGG pathway."""
        kegg_client = get_kegg_client()
        if not kegg_client:
            return "Error: KEGG Client is not initialized."

        try:
            genes = kegg_client.get_pathway_genes(pathway_id)
            if isinstance(genes, dict) and "error" in genes:
                return f"Error: {genes['error']}"
            if not genes:
                return f"No genes found for pathway '{pathway_id}'"

            output = [f"### Genes in KEGG Pathway {pathway_id}"]
            for gene in genes[:30]:
                output.append(
                    f"- **{gene.get('symbol', gene.get('id', 'N/A'))}**: "
                    f"{gene.get('description', 'N/A')}"
                )
            if len(genes) > 30:
                output.append(f"... and {len(genes) - 30} more genes")
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting pathway genes: {exc}"
