YEARS = list(range(1998, 2020))
COUNTRIES = ["us", "de"]

BASE_DATA_PATH = "../../legal-networks-data"

US_DATA_PATH = f"{BASE_DATA_PATH}/us_reg"

US_REFERENCE_PARSED_PATH = f"{US_DATA_PATH}/2_xml"
US_CROSSREFERENCE_GRAPH_PATH = f"{US_DATA_PATH}/4_crossreference_graph"
US_SNAPSHOT_MAPPING_EDGELIST_PATH = f"{US_DATA_PATH}/5_snapshot_mapping_edgelist"
US_PREPROCESSED_GRAPH_PATH = f"{US_DATA_PATH}/10_preprocessed_graph"
US_CLUSTERRESULT_PATH = f"{US_DATA_PATH}/11_cluster_results"
US_CLUSTEREVOLUTION_PATH = f"{US_DATA_PATH}/13_cluster_evolution_graph"

DE_DATA_PATH = f"{BASE_DATA_PATH}/de_reg"

DE_REFERENCE_PARSED_PATH = f"{DE_DATA_PATH}/2_xml"
DE_CROSSREFERENCE_GRAPH_PATH = f"{DE_DATA_PATH}/4_crossreference_graph"
DE_SNAPSHOT_MAPPING_EDGELIST_PATH = f"{DE_DATA_PATH}/5_snapshot_mapping_edgelist"
DE_PREPROCESSED_GRAPH_PATH = f"{DE_DATA_PATH}/10_preprocessed_graph"
DE_CLUSTERRESULT_PATH = f"{DE_DATA_PATH}/11_cluster_results"
DE_CLUSTEREVOLUTION_PATH = f"{DE_DATA_PATH}/13_cluster_evolution_graph"
