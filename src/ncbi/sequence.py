import os
from Bio import Entrez, SeqIO


def fetch_sequence(accession: str, seq_type: str = "nucleotide") -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return {"error": "NCBI_EMAIL environment variable is not set."}
        
        api_key = os.getenv("NCBI_API_KEY")
        if api_key:
            Entrez.api_key = api_key
        
        clean_acc = accession.strip().replace("'", "").replace('"', "")
        
        db = "protein" if seq_type.lower() == "protein" else "nucleotide"
        rettype = "fasta" if seq_type.lower() == "protein" else "gb"
        
        handle = Entrez.efetch(
            db=db,
            id=clean_acc,
            rettype=rettype,
            retmode="text"
        )
        
        if rettype == "gb":
            record = SeqIO.read(handle, "genbank")
            features = []
            for feat in record.features[:5]:
                if feat.type in ["gene", "CDS", "mRNA"]:
                    feat_info = {
                        "type": feat.type,
                        "location": str(feat.location),
                    }
                    if "gene" in feat.qualifiers:
                        feat_info["gene"] = feat.qualifiers["gene"][0]
                    if "product" in feat.qualifiers:
                        feat_info["product"] = feat.qualifiers["product"][0]
                    features.append(feat_info)
            
            result = {
                "accession": record.id,
                "description": record.description,
                "organism": record.annotations.get("organism", "Unknown"),
                "length": len(record.seq),
                "sequence": str(record.seq)[:500] + ("..." if len(record.seq) > 500 else ""),
                "features": features,
                "full_sequence_length": len(record.seq)
            }
        else:
            record = SeqIO.read(handle, "fasta")
            result = {
                "accession": record.id,
                "description": record.description,
                "length": len(record.seq),
                "sequence": str(record.seq)[:500] + ("..." if len(record.seq) > 500 else ""),
                "full_sequence_length": len(record.seq)
            }
        
        handle.close()
        return result
        
    except Exception as e:
        return {"error": f"Failed to fetch sequence: {str(e)}"}


def get_gene_info(gene_symbol: str, organism: str = "human") -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return {"error": "NCBI_EMAIL environment variable is not set."}
        
        api_key = os.getenv("NCBI_API_KEY")
        if api_key:
            Entrez.api_key = api_key
        
        search_term = f"{gene_symbol}[Gene Name] AND {organism}[Organism]"
        handle = Entrez.esearch(db="gene", term=search_term, retmax=1)
        result = Entrez.read(handle)
        handle.close()
        
        id_list = result.get("IdList", [])
        if not id_list:
            return {"error": f"No gene found for '{gene_symbol}' in {organism}"}
        
        gene_id = id_list[0]
        
        handle = Entrez.efetch(db="gene", id=gene_id, rettype="xml", retmode="xml")
        gene_data = Entrez.read(handle)
        handle.close()
        
        if not gene_data:
            return {"error": f"No details found for gene ID {gene_id}"}
        
        gene_entry = gene_data[0]
        
        gene_info = {
            "gene_id": gene_id,
            "symbol": gene_symbol.upper(),
            "organism": organism,
        }
        
        if "Entrezgene_gene" in gene_entry:
            gene_ref = gene_entry["Entrezgene_gene"].get("Gene-ref", {})
            gene_info["official_symbol"] = gene_ref.get("Gene-ref_locus", gene_symbol)
            gene_info["full_name"] = gene_ref.get("Gene-ref_desc", "N/A")
            
            synonyms = gene_ref.get("Gene-ref_syn", [])
            if synonyms:
                gene_info["aliases"] = list(synonyms)[:5]
        
        if "Entrezgene_summary" in gene_entry:
            summary = gene_entry["Entrezgene_summary"]
            gene_info["summary"] = summary[:500] + "..." if len(summary) > 500 else summary
        
        if "Entrezgene_location" in gene_entry:
            loc_list = gene_entry["Entrezgene_location"]
            if loc_list:
                gene_info["chromosome"] = loc_list[0].get("Maps_display-str", "N/A")
        
        return gene_info
        
    except Exception as e:
        return {"error": f"Failed to get gene info: {str(e)}"}


def search_genes(query: str, organism: str = "human", limit: int = 10) -> list:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return [{"error": "NCBI_EMAIL environment variable is not set."}]
        
        api_key = os.getenv("NCBI_API_KEY")
        if api_key:
            Entrez.api_key = api_key
        
        search_term = f"{query} AND {organism}[Organism]"
        handle = Entrez.esearch(db="gene", term=search_term, retmax=limit)
        result = Entrez.read(handle)
        handle.close()
        
        id_list = result.get("IdList", [])
        if not id_list:
            return []
        
        handle = Entrez.esummary(db="gene", id=",".join(id_list))
        summaries = Entrez.read(handle)
        handle.close()
        
        genes = []
        docs = summaries.get("DocumentSummarySet", {}).get("DocumentSummary", [])
        
        for doc in docs:
            gene = {
                "gene_id": doc.attributes.get("uid", "N/A"),
                "symbol": doc.get("Name", "N/A"),
                "description": doc.get("Description", "N/A"),
                "chromosome": doc.get("Chromosome", "N/A"),
                "organism": doc.get("Organism", {}).get("ScientificName", organism)
            }
            genes.append(gene)
        
        return genes
        
    except Exception as e:
        return [{"error": f"Gene search failed: {str(e)}"}]
