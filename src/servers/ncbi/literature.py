from shared.clients import get_ncbi_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_literature_tools(mcp):
    @mcp.tool(title="Search PubMed papers", annotations=READ_ONLY_OPEN_WORLD)
    def search_pubmed_papers(query: str) -> str:
        """Search PubMed for scientific papers and articles."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        results = ncbi_client.search_pubmed(query)
        if not results:
            return (
                f"No PubMed results found for query: '{query}'. "
                "Try simpler keywords."
            )
        if "error" in results[0]:
            return f"Error searching PubMed: {results[0]['error']}"

        output = [f"### PubMed Search Results for '{query}'"]
        for item in results:
            authors = ", ".join(item["authors"][:3])
            if len(item["authors"]) > 3:
                authors += "..."
            output.append(f"- **PMID:{item['id']}**: {item['title']}")
            output.append(f"  *Authors: {authors}*")
            output.append(f"  *Journal: {item['journal']} ({item['pub_date']})*")
        return "\n".join(output)

    @mcp.tool(title="Advanced PubMed search", annotations=READ_ONLY_OPEN_WORLD)
    def advanced_pubmed_search(
        gene: str | None = None,
        disease: str | None = None,
        drug: str | None = None,
        year_from: int | None = None,
    ) -> str:
        """Perform a structured search in PubMed using specific filters."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            results = ncbi_client.advanced_pubmed_search(
                gene=gene,
                disease=disease,
                drug=drug,
                year_from=year_from,
                limit=10,
            )
            if not results:
                return "No articles found with the specified criteria"
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"

            criteria = []
            if gene:
                criteria.append(f"Gene: {gene}")
            if disease:
                criteria.append(f"Disease: {disease}")
            if drug:
                criteria.append(f"Drug: {drug}")
            if year_from:
                criteria.append(f"From: {year_from}")

            output = ["### PubMed Search Results"]
            output.append(f"*Criteria: {', '.join(criteria)}*")
            output.append("---")

            for article in results:
                authors = article.get("authors", [])[:2]
                author_str = ", ".join(authors)
                if len(article.get("authors", [])) > 2:
                    author_str += " et al."
                output.append(f"**{article['title'][:80]}...**")
                output.append(
                    f"*{author_str}* - {article['journal']} ({article['pub_date']})"
                )
                output.append(f"PMID: {article['id']}")
                output.append("")

            return "\n".join(output)
        except Exception as exc:
            return f"Error in advanced search: {exc}"

    @mcp.tool(title="Get PubMed abstract", annotations=READ_ONLY_OPEN_WORLD)
    def get_pubmed_abstract(pmid: str) -> str:
        """Get the abstract and details of a specific PubMed article."""
        ncbi_client = get_ncbi_client()
        if not ncbi_client:
            return "Error: NCBI Client is not initialized."

        try:
            result = ncbi_client.get_pubmed_abstract(pmid)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### {result['title']}"]
            output.append(f"**Authors:** {', '.join(result['authors'])}")
            output.append(f"**Journal:** {result['journal']} ({result['year']})")
            output.append(f"**PMID:** {result['pmid']}")
            output.append("---")
            output.append("**Abstract:**")
            output.append(result["abstract"])
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting abstract: {exc}"
