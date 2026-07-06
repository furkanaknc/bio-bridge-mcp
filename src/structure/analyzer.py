from io import StringIO

from Bio.PDB import PDBParser


def analyze_pdb_text(pdb_text: str) -> dict:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", StringIO(pdb_text))

    atom_count = 0
    residue_count = 0
    chain_ids = []
    ligands = set()
    protein_name = None

    for line in pdb_text.splitlines():
        if line.startswith("TITLE") and protein_name is None:
            protein_name = line[10:].strip()

    for model in structure:
        for chain in model:
            chain_ids.append(chain.id)
            for residue in chain:
                hetfield = residue.id[0].strip()
                if hetfield == "":
                    residue_count += 1
                elif residue.resname not in {"HOH", "WAT"}:
                    ligands.add(residue.resname.strip())

                for _atom in residue:
                    atom_count += 1

    return {
        "protein": protein_name or "Unknown",
        "chains": len(set(chain_ids)),
        "atoms": atom_count,
        "residues": residue_count,
        "ligands": sorted(ligands),
    }
