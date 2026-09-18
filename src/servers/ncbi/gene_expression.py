from shared.clients import get_ncbi_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_gene_expression_tools(mcp):
    @mcp.tool(title="Search GEO datasets", annotations=READ_ONLY_OPEN_WORLD)
    def search_geo_datasets(query: str) -> str:
        """Search for gene expression datasets in NCBI GEO."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        results = ncbi_client.search_geo(query)
        if not results:
            return f"No GEO results found for query: '{query}'"

        output = [f"### GEO Search Results for '{query}'"]
        for item in results:
            output.append(f"- **{item['id']}**: {item['title']}")
            output.append(
                "  *"
                f"{item.get('organism', 'Unknown')} | "
                f"{item.get('type', 'Unknown')} | "
                f"{item.get('samples', 0)} samples*"
            )
        return "\n".join(output)

    @mcp.tool(title="Analyze GEO series", annotations=READ_ONLY_OPEN_WORLD)
    def analyze_geo_series(gse_id: str) -> str:
        """Get experiment details for a GEO series accession."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.analyze_geo_series(gse_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### GEO Series: {result['accession']}"]
            output.append(f"**Title:** {result.get('title', 'N/A')}")
            output.append(f"**Platform:** {result.get('platform', 'N/A')}")
            output.append(f"**Samples:** {result.get('sample_count', 0)}")
            output.append("---")

            if result.get("summary"):
                output.append(f"**Summary:** {result['summary'][:300]}...")
            if result.get("overall_design"):
                output.append(f"**Design:** {result['overall_design'][:200]}...")

            samples = result.get("samples", [])[:10]
            if samples:
                output.append("**Sample IDs (first 10):**")
                output.append(", ".join(samples))

            output.append("")
            output.append("*Use `classify_geo_samples` to analyze sample conditions.*")
            return "\n".join(output)
        except Exception as exc:
            return f"Error analyzing series: {exc}"

    @mcp.tool(title="Classify GEO samples", annotations=READ_ONLY_OPEN_WORLD)
    def classify_geo_samples(gse_id: str) -> str:
        """Classify samples in a GEO series into control and treated groups."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.classify_geo_samples(gse_id, max_samples=10)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### Sample Classification for {result['accession']}"]
            output.append(f"**Title:** {result.get('title', 'N/A')}")
            output.append(f"**Total Samples:** {result.get('total_samples', 0)}")
            output.append(f"**Analyzed:** {result.get('analyzed_samples', 0)}")
            output.append("---")

            controls = result.get("control", [])
            treated = result.get("treated", [])
            unknown = result.get("unknown", [])

            if controls:
                output.append(f"**Control Samples ({len(controls)}):**")
                for sample in controls[:5]:
                    output.append(f"- {sample['id']}: {sample['title'][:40]}...")

            if treated:
                output.append(f"**Treated Samples ({len(treated)}):**")
                for sample in treated[:5]:
                    dosage = f" [{sample['dosage']}]" if sample.get("dosage") else ""
                    output.append(f"- {sample['id']}: {sample['title'][:40]}...{dosage}")

            if unknown:
                output.append(
                    f"**Unknown ({len(unknown)}):** "
                    + ", ".join(sample["id"] for sample in unknown[:5])
                )

            return "\n".join(output)
        except Exception as exc:
            return f"Error classifying samples: {exc}"
