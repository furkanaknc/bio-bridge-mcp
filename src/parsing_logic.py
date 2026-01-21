import re
from Bio import Entrez
import xml.etree.ElementTree as ET

import os
from dotenv import load_dotenv

load_dotenv()

Entrez.email = os.getenv("NCBI_EMAIL")


def get_geo_sample_metadata(geo_accession: str) -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                 return {"error": "Configuration Error: NCBI_EMAIL is not set. Please configure it in your .env file or MCP client settings."}

        search_handle = Entrez.esearch(db="gds", term=geo_accession, retmax=1)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        if not search_results['IdList']:
            return {"error": f"No record found for accession {geo_accession}"}
        
        geo_uid = search_results['IdList'][0]

        handle = Entrez.esummary(db="gds", id=geo_uid)
        record = Entrez.read(handle)
        handle.close()

        if not record:
            return {"error": f"No summary data found for {geo_accession} (UID: {geo_uid})"}
        
        
        item = record[0]

        title = item.get('title', item.get('Title', ''))
        summary = item.get('summary', item.get('Summary', ''))
        
        
        full_text = f"{title} {summary}".lower()
        
        
        condition = "Unknown"
        control_keywords = ['control', 'placebo', 'untreated', 'vehicle', 'mock', 'naive', 'baseline', 'normal', 'healthy']
        treated_keywords = ['treated', 'drug', 'dose', 'exposure', 'administered', 'stimulation', 'infected', 'patient', 'disease']
        
        if any(keyword in full_text for keyword in control_keywords):
            condition = "Control"
        
        if any(keyword in full_text for keyword in treated_keywords):
            condition = "Treated"
        
        dosage = None
        dosage_pattern = re.compile(r"(\d+(\.\d+)?)\s*(mg\/kg|ug\/kg|ng\/kg|g\/kg|mg\/ml|ug\/ml|ng\/ml|uM|mM|nM|pM|M\b|%)", re.IGNORECASE)
        match = dosage_pattern.search(full_text)
        if match:
            dosage = match.group(0)

        organism = item.get('taxon', item.get('Taxon', 'Unknown'))
        
        return {
            "accession": geo_accession,
            "title": title,
            "condition": condition,
            "dosage": dosage,
            "organism": organism,
            "summary": summary[:500] + "..." if len(summary) > 500 else summary
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Parsing logic script ready.")
