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
