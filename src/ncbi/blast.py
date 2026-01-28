from Bio.Blast import NCBIWWW, NCBIXML


def run_blast(
    sequence: str,
    database: str = "nt",
    program: str = "blastn",
    max_hits: int = 10,
    expect: float = 10.0
) -> dict:
    try:
        valid_programs = ['blastn', 'blastp', 'blastx', 'tblastn', 'tblastx']
        if program not in valid_programs:
            return {"error": f"Invalid program '{program}'. Valid options: {valid_programs}"}
        
        clean_seq = ''.join(c for c in sequence if c.isalpha())
        
        if len(clean_seq) < 10:
            return {"error": "Sequence too short. Minimum 10 characters required."}
        
        if len(clean_seq) > 5000:
            return {"error": "Sequence too long. Maximum 5000 characters for web BLAST."}
        
        result_handle = NCBIWWW.qblast(
            program=program,
            database=database,
            sequence=clean_seq,
            hitlist_size=max_hits,
            expect=expect
        )
        
        blast_records = NCBIXML.parse(result_handle)
        blast_record = next(blast_records)
        
        hits = []
        for alignment in blast_record.alignments[:max_hits]:
            for hsp in alignment.hsps[:1]:
                align_len = hsp.align_length if hsp.align_length > 0 else 1
                query_len = len(clean_seq) if len(clean_seq) > 0 else 1
                hit = {
                    "title": alignment.title[:100] + "..." if len(alignment.title) > 100 else alignment.title,
                    "accession": alignment.accession,
                    "length": alignment.length,
                    "score": hsp.score,
                    "e_value": hsp.expect,
                    "identity": f"{hsp.identities}/{hsp.align_length} ({100*hsp.identities/align_len:.1f}%)",
                    "query_coverage": f"{hsp.align_length}/{len(clean_seq)} ({100*hsp.align_length/query_len:.1f}%)"
                }
                hits.append(hit)
        
        result_handle.close()
        
        return {
            "program": program,
            "database": database,
            "query_length": len(clean_seq),
            "hits_found": len(hits),
            "hits": hits
        }
        
    except Exception as e:
        return {"error": f"BLAST search failed: {str(e)}"}


def quick_blast(sequence: str) -> dict:
    clean_seq = ''.join(c for c in sequence.upper() if c.isalpha())
    
    nucleotide_chars = set('ATCGN')
    seq_chars = set(clean_seq)
    
    if seq_chars.issubset(nucleotide_chars):
        return run_blast(clean_seq, database="nt", program="blastn")
    else:
        return run_blast(clean_seq, database="nr", program="blastp")
