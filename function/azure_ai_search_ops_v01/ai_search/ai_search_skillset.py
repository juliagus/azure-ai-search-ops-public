import requests
import json

import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

def _prep_update_definition_json(skillset_name, skillset_def_path,
                                 openai_resource, openai_apikey, 
                                 openai_deploymentid, openai_modelname,
                                 target_index_name):
    """ Update the base skillset json definition file. 
    Attributes:
        skillset_name (str): skillset name
        skillset_def_path (str): skillset definition json file path
        openai_resource (str): Azure OpenAI resource
        openai_apikey (str): Azure OpenAI API Key
        openai_deploymentid (str): Azure OpenAI deployment ID
        openai_modelname (str): Azure OpenAI model name
        target_index_name (str): target index name
    Returns:
        data (dict): final skillset definition
        success (bool): flag 
    """
    success = False
    data = {}

    try:
        # read template json file
        with open(skillset_def_path, 'r') as f:
            data = json.loads(f.read())

        data["name"] = skillset_name
        data["indexProjections"]["selectors"][0]["targetIndexName"] = target_index_name

        # pass AOAI details
        data["skills"][1]["resourceUri"] = openai_resource
        data["skills"][1]["apiKey"] = openai_apikey
        data["skills"][1]["deploymentId"] = openai_deploymentid
        data["skills"][1]["modelName"] = openai_modelname

        #print(data)
        success = True

    except Exception as e:
        log.error('Error while INDEX definition update.')
        log.error(e)

    return success, data


def create_skillset(ai_search_resource, ai_search_apikey, search_api_version,
                    skillset_name, skillset_def_path,
                    openai_resource, openai_apikey, 
                    openai_deploymentid, openai_modelname,
                    target_index_name):
    """
    Create Skillset using updated definition.
    https://learn.microsoft.com/en-us/azure/search/cognitive-search-defining-skillset
    """

    success = False
    elem = 'SKILLSET'
    log.info(f'CREATE {elem} - start.')

    # load skillset json and replace temp name with new
    success_flag, data = _prep_update_definition_json(skillset_name, skillset_def_path,
                                 openai_resource, openai_apikey, openai_deploymentid, openai_modelname,
                                 target_index_name)

    if not success_flag:
         log.error(f'AI Search {elem} schema is not updated successfully. {elem} will not be created.')
         return False

    # POST https://[service name].search.windows.net/skillsets?api-version=2024-07-01
    # Content-Type: application/json  
    # api-key: [admin key]
    try: 
        headers = {
                "Content-Type": "application/json",
                "api-key": ai_search_apikey
            }

        url = f"{ai_search_resource}/skillsets?api-version={search_api_version}"

        # create skillset request
        rr = requests.post(url=url, headers=headers, data=json.dumps(data))

        if rr.status_code in [200, 201]:
            log.info(f"[{rr.status_code}]: '{skillset_name}' {elem} created OK")
            success = True
                
        else: 
            log.error(f"[{rr.status_code}]: '{skillset_name}' {elem} is NOT created.")
            log.error(rr.text)

        log.info(f'CREATE {elem} - end.')
        
    except Exception as e:
        log.error(e)

    log.info('skillset code before return: %s' %success)
    return success


if __name__ == '__main__':
    with open('../config.json', 'r') as f:
        config = json.loads(f.read())
    
    ai_search_resource = config["AISearchEndpoint"]
    ai_search_apikey = config["AISearchAPIKey"]
    search_api_version = '2024-07-01'
    skillset_name = 'test-skillset-02'
    skillset_def_path = './data/vector-index/ai_search_skillset_vector_def_v2.json'
    openai_resource = config["AOAIResource"]
    openai_apikey = config["AOAIAPIKEY"]
    openai_deploymentid = config["AOAIDeploymentID"]
    openai_modelname = config["AOAIModelName"]
    target_index_name = 'simple-index-release03'

    create_skillset(ai_search_resource, ai_search_apikey, search_api_version,
                   skillset_name, skillset_def_path,
                    openai_resource, openai_apikey, openai_deploymentid, openai_modelname,
                    target_index_name)
    