import os
import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

import azure.functions as func

#import ai_search.ai_search_ops as ais_ops
from azure_ai_search_ops_v01.ai_search import ai_search_ops 


def load_config():
    """Load Env Vars"""
    config = {}
    for c in ["AISearchEndpoint", "AISearchAPIKey", "StorageAcc",
              "StorageAccConnStr", "StorageAccContainer",
              "StorageAccFolder", "AOAIResource",
              "AOAIAPIKEY", "AOAIDeploymentID", "AOAIModelName"]:
        config[c] = os.environ[c]
    return config

def main(req: func.HttpRequest) -> func.HttpResponse:
    log.info('Python HTTP trigger function processed a request.')

    try:

        #load env vars into config
        config = load_config()

        base_index_name = 'vect-index'
        #release_name = 'release-11'
        release_name = os.environ["RELEASE_NAME"]
        #folder = os.getcwd()
    
        # definition jsons
        index_schema_path = './azure_ai_search_ops_v01/data/vector-index/ai_search_index_schema.json'
        indexer_def_path = './azure_ai_search_ops_v01/data/vector-index/ai_search_indexer_vector_def_v2.json'
        skillset_def_path = './azure_ai_search_ops_v01/data/vector-index/ai_search_skillset_vector_def_v2.json'
        vectorize_flag = True
        
        aisearchops = ai_search_ops.AISearchOps(config=config, 
                                    base_index_name=base_index_name, 
                                    release_name=release_name,
                                    index_schema_path=index_schema_path,
                                    indexer_def_path=indexer_def_path,
                                    vectorize_flag=vectorize_flag,
                                    skillset_def_path=skillset_def_path)
        success = aisearchops.create_search()
        
        if success:
            return func.HttpResponse('Azure AI Search configuration created OK.', status_code=200)
        else:
            return func.HttpResponse('Azure AI Search configuration contains ERRORS.', status_code=400)
        

    except Exception as e:
        error_msg = "Exception while configuring Azure AI Search."
        log.error(e)
        return func.HttpResponse(
             error_msg,
             status_code=400
        )