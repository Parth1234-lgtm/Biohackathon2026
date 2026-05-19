import pandas as pd
import decoupler as dc
import re
import json
from bioservices import UniProt

from dataclasses import dataclass, field, asdict
from typing import Optional

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class SoldierGene:
    """Downstream/co-regulated gene that produces a detectable blood protein."""
    gene_name: str
    
    # Protein info from UniProt (filled in Stage 5)
    uniprot_id: Optional[str] = None
    protein_name: Optional[str] = None
    alternative_names: list = field(default_factory=list)
    function: Optional[str] = None
    sequence_length: Optional[int] = None
    subcellular_location: Optional[str] = None
    pdb_structures: list = field(default_factory=list)


@dataclass
class SusGene:
    """A PCOS-suspicious main gene from DE analysis or literature."""
    
    # ----- Identity & evidence (Stage 1) -----
    gene_name: str
    tier: str                                      # "tier-1" / "tier-2" / "literature_only"
    lfc_mean: Optional[float] = None
    proba_m1: Optional[float] = None
    
    # ----- Regulatory network (Stage 2) -----
    scenario: Optional[str] = None                 # "A" / "B" / "unknown"
    regulating_tf: Optional[str] = None            # name of TF; "self" if Scenario B
    soldier_genes: list = field(default_factory=list)   # list of SoldierGene objects
    
    # ----- Protein info from UniProt (Stage 3) -----
    uniprot_id: Optional[str] = None
    protein_name: Optional[str] = None
    alternative_names: list = field(default_factory=list)
    function: Optional[str] = None
    sequence_length: Optional[int] = None
    subcellular_location: Optional[str] = None
    pdb_structures: list = field(default_factory=list)


#----------------------------------STAGE-1:LOAD--------------------------------------------------------------------------------#

df1=pd.read_csv("cluster5_tier1.csv")
df2=pd.read_csv("cluster5_tier2.csv")

tier1_20=df1.sort_values(by='lfc_mean',ascending=False).head(20)[['gene','lfc_mean','proba_m1']]
tier2_20=df2.sort_values(by='lfc_mean',ascending=False).head(20)[['gene','lfc_mean','proba_m1']]

dict_t1:dict=tier1_20.to_dict()
dict_t2:dict=tier2_20.to_dict()

sus_gene_cl5={}

for i,gene in dict_t1['gene'].items():
    sus_gene_cl5[gene]=SusGene(gene_name=gene,tier='tier-1',lfc_mean=dict_t1['lfc_mean'][i],proba_m1=dict_t1['proba_m1'][i])

for i,gene in dict_t2['gene'].items():
    sus_gene_cl5[gene]=SusGene(gene_name=gene,tier='tier-2',lfc_mean=dict_t2['lfc_mean'][i],proba_m1=dict_t2['proba_m1'][i])



#----------------------------------STAGE-2:CLASSIFY & SOLDIER--------------------------------------------------------------------------------#


def get_top_soldiers(tf_name, dorothea_df, sus_gene_dict, exclude_self=None, n=10):
    """Get top N soldier genes for a given TF, prioritizing sus-list overlap."""
    
    # All activated targets of this TF
    all_targets = dorothea_df[
        (dorothea_df['source'] == tf_name) &
        (dorothea_df['weight'] > 0)  &
        (dorothea_df['confidence']=='A')                  # activators only
    ]['target'].tolist()
    
    # Exclude self (when classifying the main sus_gene, don't list itself as soldier)
    if exclude_self:
        all_targets = [t for t in all_targets if t != exclude_self]
    
    # Priority 1: targets that are ALSO in your suspicious gene list
    overlap = [t for t in all_targets if t in sus_gene_dict]
    
    # Priority 2: fill remaining slots from non-overlap targets
    remaining = [t for t in all_targets if t not in overlap]
    
    # Combine: overlap first, then fill
    top_soldiers = overlap[:n] + remaining[:n - len(overlap)]
    
    return top_soldiers[:n]


def classify_and_get_soldiers(sus_gene:SusGene, dorothea_df, sus_gene_dict):
    
    is_tf = sus_gene.gene_name in dorothea_df['source'].unique()
    
    if is_tf:
        # Get this gene's downstream targets (activators only)
        targets = dorothea_df[
            (dorothea_df['source'] == sus_gene.gene_name) & 
            (dorothea_df['weight'] > 0) & (dorothea_df['confidence']=='A')
        ]['target'].tolist()
        
        # Check if it drives any other sus genes → Scenario B
        suspicious_targets = [t for t in targets if t in sus_gene_dict]
        
        if len(suspicious_targets) > 0:
            sus_gene.scenario = "B"
            sus_gene.regulating_tf = "self"
            
            # Soldiers are this gene's own downstream targets
            soldier_names = get_top_soldiers(
                tf_name=sus_gene.gene_name,
                dorothea_df=dorothea_df,
                sus_gene_dict=sus_gene_dict,
                exclude_self=sus_gene.gene_name,
                n=10
            )
            sus_gene.soldier_genes = [SoldierGene(gene_name=g) for g in soldier_names]
            return
    
    # Default: Scenario A
    upstream = dorothea_df[
        (dorothea_df['target'] == sus_gene.gene_name) &
        (dorothea_df['weight'] > 0) & (dorothea_df['confidence']=='A')
    ]
    
    if upstream.empty:
        sus_gene.scenario = "unknown"
        return
    
    # Pick the first upstream TF (or could prioritize sus-list TFs here too)
    main_tf = upstream.iloc[0]['source']
    
    sus_gene.scenario = "A"
    sus_gene.regulating_tf = main_tf
    
    # Soldiers are co-targets of the main TF, excluding self
    soldier_names = get_top_soldiers(
        tf_name=main_tf,
        dorothea_df=dorothea_df,
        sus_gene_dict=sus_gene_dict,
        exclude_self=sus_gene.gene_name,
        n=10
    )
    sus_gene.soldier_genes = [SoldierGene(gene_name=g) for g in soldier_names]


dorothea_df = dc.op.dorothea(organism='human', levels=['A', 'B', 'C'])

for gene,obj in sus_gene_cl5.items():
    classify_and_get_soldiers(obj,dorothea_df,sus_gene_cl5)



#----------------------------------STAGE-3:PROTIN INFO--------------------------------------------------------------------------------#

def get_protien_info(susgene: SusGene, uniprot):
    gene_query = f"gene:{susgene.gene_name} AND organism_id:9606"

    # Use the exact columns that generated your dictionary keys successfully
    query_columns = "accession,protein_name,cc_function,length,cc_subcellular_location,xref_pdb"
    res = uniprot.search(gene_query, frmt="tsv", columns=query_columns)

    if not res:
        return

    lines = res.strip().split('\n')
    if len(lines) <= 1:
        return  # No data row found

    # 1. Zip the headers and values directly into a clean dictionary
    headers = lines[0].split('\t')
    values = lines[1].split('\t')
    data_map = dict(zip(headers, values))

    # 2. Extract directly from the keys shown in your dictionary screenshot
    
    # UniProt ID (Key: 'Entry')
    if 'Entry' in data_map and data_map['Entry'].strip():
        susgene.uniprot_id = data_map['Entry'].strip()

    # Function (Key: 'Function [CC]')
    if 'Function [CC]' in data_map and data_map['Function [CC]'].strip():
        susgene.function = data_map['Function [CC]'].strip()

    # Sequence Length (Key: 'Length')
    if 'Length' in data_map and data_map['Length'].strip():
        susgene.sequence_length = int(data_map['Length'].strip())

    # Subcellular Location (Key: 'Subcellular location [CC]')
    if 'Subcellular location [CC]' in data_map and data_map['Subcellular location [CC]'].strip():
        susgene.subcellular_location = data_map['Subcellular location [CC]'].strip()

    # PDB Structures (Key: 'PDB')
    if 'PDB' in data_map and data_map['PDB'].strip():
        raw_pdb = data_map['PDB'].strip()
        susgene.pdb_structures = [s.strip() for s in raw_pdb.split(';') if s.strip()]

    # Protein Name & Aliases (Key: 'Protein names')
    if 'Protein names' in data_map and data_map['Protein names'].strip():
        txt = data_map['Protein names'].strip()
        main_name = txt.split("(")[0].strip()
        aliases = re.findall(r"\((.*?)\)", txt)

        susgene.protein_name = main_name
        susgene.alternative_names = aliases


uniprot=UniProt(verbose=False)

#get protien info for every gene(main+soldier)
for gene,obj in sus_gene_cl5.items():
    get_protien_info(obj,uniprot)
    for o in obj.soldier_genes:
        get_protien_info(o,uniprot)

#flatten the dataclasses
for gene,obj in sus_gene_cl5.items():
    
    if type(obj) is not dict:
        try:
            sus_gene_cl5[gene]=asdict(obj)
        except:
            print(gene,obj)

        l=[asdict(o) for o in obj.soldier_genes ]
        obj.soldier_genes=l


#save the final json file
with open(r'..\final_look_up.json','w') as f:
    json.dump(sus_gene_cl5,f,indent=3)