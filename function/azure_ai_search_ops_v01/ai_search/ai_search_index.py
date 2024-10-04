import datetime
import requests
import json

import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')


def _prep_update_definition_json(index_name, index_schema_path, vectorize_flag,
                                 openai_resource=None, openai_apikey=None, 
                                 openai_deploymentid=None, openai_modelname=None):
    """ Update the base index definition file. 
    Attributes:
        ndex_name
        index_schema_path
        vectorize_flag (bool): indicates is vectorization is part of the process
        openai_resource (str): Azure OpenAI resource
        openai_apikey (str): Azure OpenAI API key
        openai_deploymentid (str): Azure OpenAI deployment ID
        openai_modelname (str): Azure OpenAI model name
    Returns:
        data (dict): index definition json
        success (bool): indicates if index definition was created ok
    """

    success = True
    data = {}

    try:
        with open(index_schema_path, 'r') as f:
            data = json.loads(f.read())

        data["name"] = index_name
        
        if vectorize_flag and ("vectorSearch" in data.keys()):
            # vector index is created

            # update vectorizer name
            vectorizer_name = f'vectorizer-AOAI-text-{index_name}'
            data["vectorSearch"]["vectorizers"][0]["name"] = vectorizer_name

            # update vectorizer
            if openai_resource is not None and openai_apikey is not None and openai_deploymentid is not None and openai_modelname is not None:
                data["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]["resourceUri"] = openai_resource
                data["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]["deploymentId"] = openai_deploymentid
                data["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]["apiKey"] = openai_apikey
                data["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]["modelName"] = openai_modelname
            else:
                log.error('Azure OpenAI resource details are not provided.')
                return  False, {}
            
            # update profiles 
            data["vectorSearch"]["profiles"][0]["vectorizer"] = vectorizer_name
            profile_name = f'profile-AOAI-text-{index_name}'
            data["vectorSearch"]["profiles"][0]["name"] = profile_name

            # check vector fields have correct vector profile
            for field in data["fields"]:
                if field["vectorSearchProfile"] is not None:
                    field["vectorSearchProfile"] = profile_name

            # add vectoriser details
            # print('vector index')
            # print(f'\n\n{data["vectorSearch"]}\n\n')

        # save locally index definition file - if needed
        # with open('./data/vector-index/ai_search_index_schema_OUT.json', 'w') as f:
        #     f.write(json.dumps(data, indent=4))
        success = True

    except Exception as e:
        log.error('Error while INDEX definition update.')
        log.error(e)
         
    return success, data


def create_index(ai_search_resource, ai_search_apikey, search_api_version, index_schema_path,
                 search_index_name,
                 vectorize_flag,
                 openai_resource=None, openai_apikey=None, 
                 openai_deploymentid=None, openai_modelname=None):
    """ Create index based on the updated definition.
    https://learn.microsoft.com/en-us/rest/api/searchservice/create-index 
    https://learn.microsoft.com/en-us/rest/api/searchservice/indexes/create?view=rest-searchservice-2024-07-01&tabs=HTTP

    """
    success = False
    elem = 'INDEX'
    log.info(f'CREATE {elem} - start.')

    # update final definition json
    success_flag, data = _prep_update_definition_json(search_index_name, index_schema_path,
                                                      vectorize_flag,
                                                      openai_resource, openai_apikey, 
                                                      openai_deploymentid, openai_modelname)
    if not success_flag:
         log.error('AI Search index schema is not updated successfully. Index will not be created.')
         return False

    # POST https://[servicename].search.windows.net/indexes?api-version=[api-version]  
    # Content-Type: application/json
    # api-key: [admin key]
    try: 
        headers = {
                "Content-Type": "application/json",
                "api-key": ai_search_apikey
            }

        url = f"{ai_search_resource}/indexes?api-version={search_api_version}"

        rr = requests.post(url=url, headers=headers, data=json.dumps(data))

        if rr.status_code in [200, 201]:
                log.info(f"[{rr.status_code}]: '{search_index_name}' index created OK.")
                success = True
                
        else: 
                log.error(f"[{rr.status_code}]: '{search_index_name}' index is NOT created.")
                log.error(rr.text)

        log.info(f'CREATE {elem} - end.')
        
    except Exception as e:
        log.error(e)

    return success


def check_index_exists(ai_search_resource, ai_search_apikey, search_api_version, search_index_name):
    """Check if the index exists"""
    #GET https://myservice.search.windows.net/indexes('hotels')?api-version=2024-07-01

    log.info(f"CHECK INDEX exists {search_index_name}.")

    headers = {
            #"Content-Type": "application/json",
            "api-key": ai_search_apikey
        }
    url = f"{ai_search_resource}/indexes('{search_index_name}')?api-version={search_api_version}"
    #print(url)

    rr = requests.get(url=url, headers=headers)
    if rr.status_code in [404]:
        #index doesn't exist
        #log.info(f"Index doesn't exist - {self.search_index_name}")
        log.info(json.loads(rr.text)["error"]["message"])
        return False
    else: 
        log.info("Index '%s' exists." %search_index_name)
        return True

if __name__ == '__main__':
    with open('../config.json', 'r') as f:
        config = json.loads(f.read())
    
    ai_search_resource = config["AISearchEndpoint"]
    ai_search_apikey = config["AISearchAPIKey"]
    search_api_version = '2024-07-01'
    index_schema_path = './data/vector-index/ai_search_index_schema.json'

    # skillset_name = 'test-skillset-02'
    # skillset_def_path = './data/vector-index/ai_search_skillset_vector_def_v2.json'
    # openai_resource = config["AOAIResource"]
    # openai_apikey = config["AOAIAPIKEY"]
    # openai_deploymentid = config["AOAIDeploymentID"]
    # openai_modelname = config["AOAIModelName"]
    search_index_name = 'simple-index-release03vect'


    create_index(ai_search_resource, ai_search_apikey, search_api_version, index_schema_path,
                 search_index_name)