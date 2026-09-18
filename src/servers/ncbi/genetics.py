from shared.clients import get_ncbi_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_genetics_tools(mcp):
    @mcp.tool(title="Run NCBI BLAST", annotations=READ_ONLY_OPEN_WORLD)
    def blast_sequence(
        sequence: str,
        database: str = "nt",
        program: str = "blastn",
    ) -> str:
        """Run a BLAST search to find matching sequences in the NCBI database."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.blast_sequence(sequence, database, program)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### BLAST Results ({result['program']} vs {result['database']})"]
            output.append(f"**Query Length:** {result['query_length']} bp")
            output.append(f"**Hits Found:** {result['hits_found']}")
            output.append("---")

            for index, hit in enumerate(result["hits"][:5], start=1):
                output.append(f"**{index}. {hit['accession']}**")
                output.append(f"   {hit['title']}")
                output.append(f"   - E-value: {hit['e_value']:.2e}")
                output.append(f"   - Identity: {hit['identity']}")
                output.append(f"   - Coverage: {hit['query_coverage']}")

            return "\n".join(output)
        except Exception as exc:
            return f"Error running BLAST: {exc}"

    @mcp.tool(title="Fetch NCBI sequence", annotations=READ_ONLY_OPEN_WORLD)
    def fetch_sequence(accession: str, seq_type: str = "nucleotide") -> str:
        """Fetch a DNA, RNA, or protein sequence from NCBI."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.fetch_sequence(accession, seq_type)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### Sequence: {result['accession']}"]
            output.append(f"**Description:** {result['description']}")
            if "organism" in result:
                output.append(f"**Organism:** {result['organism']}")
            output.append(f"**Length:** {result['full_sequence_length']} bp")
            output.append("---")

            features = result.get("features", [])
            if features:
                output.append("**Features:**")
                for feature in features:
                    feature_text = f"- {feature['type']}"
                    if "gene" in feature:
                        feature_text += f" ({feature['gene']})"
                    if "product" in feature:
                        feature_text += f": {feature['product']}"
                    output.append(feature_text)
                output.append("---")

            output.append("**Sequence (first 500 bp):**")
            output.append(f"```\n{result['sequence']}\n```")
            return "\n".join(output)
        except Exception as exc:
            return f"Error fetching sequence: {exc}"

    @mcp.tool(title="Get NCBI gene details", annotations=READ_ONLY_OPEN_WORLD)
    def get_gene_info(gene_symbol: str, organism: str = "human") -> str:
        """Get detailed information about a specific gene."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.get_gene_info(gene_symbol, organism)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### Gene: {result.get('official_symbol', gene_symbol)}"]
            output.append(f"**Full Name:** {result.get('full_name', 'N/A')}")
            output.append(f"**Gene ID:** {result.get('gene_id', 'N/A')}")
            output.append(f"**Organism:** {result.get('organism', organism)}")

            if "chromosome" in result:
                output.append(f"**Chromosome:** {result['chromosome']}")
            if "aliases" in result:
                output.append(f"**Aliases:** {', '.join(result['aliases'])}")

            output.append("---")
            if "summary" in result:
                output.append("**Summary:**")
                output.append(result["summary"])
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting gene info: {exc}"

    @mcp.tool(title="Search NCBI genes", annotations=READ_ONLY_OPEN_WORLD)
    def search_genes(query: str, organism: str = "human") -> str:
        """Search for genes by keyword."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            results = ncbi_client.search_genes(query, organism, limit=10)
            if not results:
                return f"No genes found for '{query}' in {organism}"
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"

            output = [f"### Gene Search Results for '{query}' ({organism})"]
            for gene in results:
                output.append(f"- **{gene['symbol']}** (ID: {gene['gene_id']})")
                output.append(f"  {gene['description']}")
                if gene.get("chromosome") != "N/A":
                    output.append(f"  *Chromosome: {gene['chromosome']}*")

            output.append("")
            output.append("*Use `get_gene_info` for detailed information about a specific gene.*")
            return "\n".join(output)
        except Exception as exc:
            return f"Error searching genes: {exc}"
