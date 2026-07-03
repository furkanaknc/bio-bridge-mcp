from servers.alphafold.structures import register_alphafold_tools
from servers.clinvar.variants import register_clinvar_tools
from servers.kegg.pathways import register_kegg_tools
from servers.ncbi.gene_expression import register_gene_expression_tools
from servers.ncbi.genetics import register_genetics_tools
from servers.ncbi.literature import register_literature_tools
from servers.rcsb.structures import register_rcsb_tools
from servers.uniprot.proteins import register_uniprot_tools


def register_all_tools(mcp):
    register_literature_tools(mcp)
    register_gene_expression_tools(mcp)
    register_genetics_tools(mcp)
    register_rcsb_tools(mcp)
    register_uniprot_tools(mcp)
    register_kegg_tools(mcp)
    register_alphafold_tools(mcp)
    register_clinvar_tools(mcp)
