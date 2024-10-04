import requests
import json

import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

def _prep_indexer_def_json(indexer_name, indexer_def_path,
                   data_source_name, target_index_name, 
                   skillset_name):
    """ Update the base indexer json definition file
    Attributes:
        indexer_name (str): indexer name 
        indexer_def_path (str): path to base indexer definition json file
        data_source_name (str): data source name 
        target_index_name (str): target index name
        skillset_name (str): skillset name
    Returns:
        data (dict): final indexer definition
    """
    success = False
    data = {}

    try:
        with open(indexer_def_path, 'r') as f:
            data = json.loads(f.read())

        data["name"] = indexer_name
        data["dataSourceName"] = data_source_name
        data["targetIndexName"] = target_index_name
        data["skillsetName"] = skillset_name

        #print(data)
        success = True
    except Exception as e:
        log.error('Error while INDEXER definition update.')
        log.error(e)

    return success, data


def create_indexer(ai_search_resource, ai_search_apikey, search_api_version,
                   indexer_name, indexer_def_path,
                   data_source_name, target_index_name, skillset_name):
    """ Create Indexer based on the definition. This requires data source, skill set and target index.
    https://learn.microsoft.com/en-us/rest/api/searchservice/create-indexer
    """

    success = False
    elem = 'INDEXER'
    log.info(f'CREATE {elem} - start.')

    # load indexer json and replace temp name with new
    success_flag, data = _prep_indexer_def_json(indexer_name, indexer_def_path,
                                            data_source_name, target_index_name, 
                                            skillset_name)

    if not success_flag:
        log.error(f'AI Search {elem} schema is not updated successfully. {elem} will not be created.')
        return False

    # POST https://[service name].search.windows.net/indexers?api-version=[api-version]
    # Content-Type: application/json  
    # api-key: [admin key]
    try:
        headers = {
                "Content-Type": "application/json",
                "api-key": ai_search_apikey
            }

        url = f"{ai_search_resource}/indexers?api-version={search_api_version}"
        
        # create indexer request
        rr = requests.post(url=url, headers=headers, data=json.dumps(data))

        if rr.status_code in [200, 201]:
            log.info(f"[{rr.status_code}]: '{indexer_name}' indexer created OK")
            success = True
                
        else: 
            log.error(f"[{rr.status_code}]: '{indexer_name}' indexer is NOT created.")
            log.error(rr.text)

        log.info(f'CREATE {elem} - end.')

    except Exception as e:
        log.error(e)
    
    return success