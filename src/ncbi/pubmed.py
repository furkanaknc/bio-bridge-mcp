import os
from Bio import Entrez

def search(query: str, limit: int = 5) -> list:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            
        handle = Entrez.esearch(db="pubmed", term=query, retmax=limit, sort='relevance')
        results = Entrez.read(handle)
        handle.close()
        
        id_list = results.get("IdList", [])
        if not id_list:
            return []
            
        summary_handle = Entrez.esummary(db="pubmed", id=",".join(id_list))
        summaries = Entrez.read(summary_handle)
        summary_handle.close()
        
        output = []
        for item in summaries:
            output.append({
                "id": item.get("Id"),
                "title": item.get("Title", "Unknown Title"),
                "authors": item.get("AuthorList", []),
                "journal": item.get("Source", item.get("FullJournalName", "Unknown Journal")),
                "pub_date": item.get("PubDate", "")
            })
        return output
    except Exception as e:
        return [{"error": f"PubMed search failed: {str(e)}"}]


def advanced_search(gene: str = None, disease: str = None, drug: str = None, 
                    author: str = None, year_from: int = None, year_to: int = None,
                    limit: int = 10) -> list:
    try:
        query_parts = []
        
        if gene:
            query_parts.append(f"({gene}[Gene Name] OR {gene}[Title/Abstract])")
        if disease:
            query_parts.append(f"{disease}[MeSH Terms]")
        if drug:
            query_parts.append(f"{drug}[Title/Abstract]")
        if author:
            query_parts.append(f"{author}[Author]")
        if year_from and year_to:
            query_parts.append(f"{year_from}:{year_to}[dp]")
        elif year_from:
            query_parts.append(f"{year_from}:3000[dp]")
        elif year_to:
            query_parts.append(f"1900:{year_to}[dp]")
        
        if not query_parts:
            return [{"error": "At least one search parameter required"}]
        
        query = " AND ".join(query_parts)
        return search(query, limit)
        
    except Exception as e:
        return [{"error": f"Advanced search failed: {str(e)}"}]


def get_abstract(pmid: str) -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
        
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        
        if not records.get("PubmedArticle"):
            return {"error": f"Article not found: {pmid}"}
        
        article = records["PubmedArticle"][0]
        medline = article.get("MedlineCitation", {})
        article_data = medline.get("Article", {})
        
        abstract_text = ""
        abstract_parts = article_data.get("Abstract", {}).get("AbstractText", [])
        if abstract_parts:
            if isinstance(abstract_parts[0], str):
                abstract_text = " ".join(abstract_parts)
            else:
                abstract_text = " ".join([str(p) for p in abstract_parts])
        
        authors = []
        author_list = article_data.get("AuthorList", [])
        for auth in author_list[:5]:
            name = f"{auth.get('LastName', '')} {auth.get('Initials', '')}".strip()
            if name:
                authors.append(name)
        
        return {
            "pmid": pmid,
            "title": article_data.get("ArticleTitle", ""),
            "authors": authors,
            "journal": article_data.get("Journal", {}).get("Title", ""),
            "year": medline.get("DateCompleted", {}).get("Year", ""),
            "abstract": abstract_text[:2000] if abstract_text else "No abstract available"
        }
        
    except Exception as e:
        return {"error": f"Failed to get abstract: {str(e)}"}
