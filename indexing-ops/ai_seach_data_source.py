
import requests
import json

import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

def create_data_source(ai_search_resource, ai_search_apikey, search_api_version,
                      data_src_name, data_src_connstr, data_src_container, data_src_dir):
    """ Create data source in AI Search
    https://learn.microsoft.com/en-us/azure/search/search-howto-index-azure-data-lake-storage
    https://learn.microsoft.com/en-us/rest/api/searchservice/create-data-source 

    Attributes:
        ai_search_resource (str): Azure AI Search resource
        ai_search_apikey (str): Azure AI Search API key
        search_api_version (str): Azure AI Search API version
        data_src_name (str): data source name
        data_src_connstr (str): storage account connection string
        data_src_container (str): data container
        data_src_dir (str): data folder
    Returns:
        success (bool): True if creation is successful
    """

    elem = 'DATA SOURCE'
    success = False
    log.info(f'CREATE {elem} - start.')

    # create data source definition
    data_source_def = {
        "name": data_src_name,
        "type": "adlsgen2",
        "credentials": {"connectionString": data_src_connstr},
        "container": {"name": data_src_container, "query": data_src_dir}
    }

    # POST https://[service name].search.windows.net/datasources?api-version=[api-version]  
    # Content-Type: application/json  
    # api-key: [admin key]

    try:
        headers = {
                "Content-Type": "application/json",
                "api-key": ai_search_apikey
            }

        url = f"{ai_search_resource}/datasources?api-version={search_api_version}"

        rr = requests.post(url=url, headers=headers, data=json.dumps(data_source_def))

        if rr.status_code in [200, 201]:
            log.info(f"[{rr.status_code}]: '{data_src_name}' data source created OK.")
            success = True
                
        else: 
            log.error(f"[{rr.status_code}]: '{data_src_name}' data source is NOT created.")
            log.error(rr.text)

        log.info(f'CREATE {elem} - end.')
        
    except Exception as e:
        log.error(e)
        
    return success