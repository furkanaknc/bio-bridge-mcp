def _build_client(factory, name: str):
    try:
        return factory()
    except Exception as exc:
        print(f"Warning: {name} client could not be initialized: {exc}")
        return None


class ClientRegistry:
    def __init__(self):
        self._ncbi = None
        self._rcsb = None
        self._uniprot = None
        self._kegg = None
        self._alphafold = None
        self._clinvar = None

    def get_ncbi(self):
        if self._ncbi is None:
            from ncbi.client import NcbiClient

            self._ncbi = _build_client(NcbiClient, "NCBI")
        return self._ncbi

    def get_rcsb(self):
        if self._rcsb is None:
            from rcsb.client import RcsbClient

            self._rcsb = _build_client(RcsbClient, "RCSB")
        return self._rcsb

    def get_uniprot(self):
        if self._uniprot is None:
            from uniprot.client import UniProtClient

            self._uniprot = _build_client(UniProtClient, "UniProt")
        return self._uniprot

    def get_kegg(self):
        if self._kegg is None:
            from kegg.client import KeggClient

            self._kegg = _build_client(KeggClient, "KEGG")
        return self._kegg

    def get_alphafold(self):
        if self._alphafold is None:
            from alphafold.client import AlphaFoldClient

            self._alphafold = _build_client(AlphaFoldClient, "AlphaFold")
        return self._alphafold

    def get_clinvar(self):
        if self._clinvar is None:
            from clinvar.client import ClinVarClient

            self._clinvar = _build_client(ClinVarClient, "ClinVar")
        return self._clinvar


clients = ClientRegistry()


def get_ncbi_client():
    return clients.get_ncbi()


def get_rcsb_client():
    return clients.get_rcsb()


def get_uniprot_client():
    return clients.get_uniprot()


def get_kegg_client():
    return clients.get_kegg()


def get_alphafold_client():
    return clients.get_alphafold()


def get_clinvar_client():
    return clients.get_clinvar()
