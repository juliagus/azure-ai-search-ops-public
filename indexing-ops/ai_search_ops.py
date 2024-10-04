"""
This code should be deployed as Azure Function. 
This Azure Function for release will:
1. Create a new Azure AI Search Index (which is based on a folder/ folders which contain data for another release)
2. Create OR reuse new skillset (need to see how to do this)
3. Will invoke the indexer to start processing data

Based on REST API Calls

"""
import datetime
import json

import ai_search_index as ais_index
import ai_seach_data_source as ais_datasrc
import ai_search_indexer as ais_indexer
import ai_search_skillset as ais_skillset

import logging as log
log.basicConfig(level=log.INFO, format='%(asctime)s : %(levelname)s : %(message)s')




class AISearchOps:
    def __init__(self, config, base_index_name, release_name, 
                 index_schema_path, indexer_def_path, 
                 vectorize_flag = False, 
                 skillset_def_path=''):
        """
        Create initial ai search ops object. Note that specified version of the AI Search API is used.
        This might need to be updated in the future, however re-test is needed.

        Args:
            base_index_name (str): base name of the AI search index
            release_name (str): name or version of release, used in all objects created
            index_schema_path (str): path to the json file with index definition
            indexer_def_path (str): path to the json file with indexer definition
            vectorize (bool): if there is vectorization
            skillset_def_path (str): path to the json file with skillset definition
        Returns:

        """

        self.release_name = release_name

        # AI SEARCH
        # to be loaded from config
        self.ai_search_resource = ''
        self.ai_search_apikey = ''
        self.search_api_version = '2024-07-01'
        # vectorize flag - should be AOAI resources provided, will need skillset creation
        self.vectorize_flag = vectorize_flag

        #self.ai_search_base_index_name = 'vector-index'
        self.ai_search_base_index_name = base_index_name 
        self.search_index_name = f"{self.ai_search_base_index_name}-{self.release_name}"
        self.search_indexer_name = f'indexer-adlgen2-{self.release_name}'
        self.search_skillset_name = f'skillset-vector-{self.release_name}'

        # AI Search Configs in jsons
        # v1 - simple version with index, datasource, indexer
        self.index_schema = index_schema_path
        self.indexer_def = indexer_def_path
        self.skillset_def = skillset_def_path

        # DATA SOURCE
        self.data_source_storage_acc = ''
        self.data_source_name = f'data-source-{self.release_name}'

        # to be loaded from config
        self.data_source_container = ''
        self.data_source_folder = ''
        self.data_source_conn_str = ''

        # Azure OpenAI Embeddings
        # to be loaded from config
        self.aoai_resource = ''
        self.aoai_apikey = ''
        self.aoai_deploymentid = ''
        self.aoai_modelname = ''
        
        # load resources and API keys
        self._get_config(config)

    def _get_config(self, config):
        """ 
        Retrieve config & env vars.
        """

        # AI SEARCH
        try: 
            self.ai_search_resource = config["AISearchEndpoint"]
            self.ai_search_apikey = config["AISearchAPIKey"]
            log.info('AI Search - resource details found.')
        except Exception as e:
            log.error('AI Search  - resource details NOT found.')

        # DATA SOURCE
        try: 
            self.data_source_container = config["StorageAccContainer"]
            self.data_source_folder = config["StorageAccFolder"]
            self.data_source_conn_str = config["StorageAccConnStr"]
            log.info('Data Source - resource details found.')
        except Exception as e:
            log.error('Data Source - resource details NOT found.')

        # Azure OpenAI Embeddings
        if self.vectorize_flag:
            try:
                self.aoai_resource = config["AOAIResource"]
                self.aoai_apikey = config["AOAIAPIKEY"]
                self.aoai_deploymentid = config["AOAIDeploymentID"]
                self.aoai_modelname = config["AOAIModelName"]
                log.info('Vect: Azure OpenAI - resource details found.')
            except Exception as e:
                log.error('Vect: Azure OpenAI - resource details NOT found.')
            

    def prep_index(self):
        """ Create index with needed configuration. 
        First is checked if index exists, then name will be updated.
        Returts:
        success (bool): if execution is successful
        """
        # check if index exists and create
       
        if ais_index.check_index_exists(ai_search_resource=self.ai_search_resource,
                                        ai_search_apikey=self.ai_search_apikey,
                                        search_api_version=self.search_api_version,
                                        search_index_name=self.search_index_name):
            # add time to index name and create
            dd = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            self.search_index_name += '-%s' %dd
            self.data_source_name += '-%s' %dd
            self.search_indexer_name += '-%s' %dd
            self.search_skillset_name += '-%s' %dd
            
        if self.vectorize_flag:
            # AOAI resource needed loaded
            success = ais_index.create_index(ai_search_resource=self.ai_search_resource,
                               ai_search_apikey=self.ai_search_apikey,
                               search_api_version=self.search_api_version,
                               index_schema_path=self.index_schema,
                               search_index_name=self.search_index_name,
                               vectorize_flag=self.vectorize_flag,
                               openai_resource=self.aoai_resource,
                               openai_apikey=self.aoai_apikey,
                               openai_deploymentid=self.aoai_deploymentid,
                               openai_modelname=self.aoai_modelname)
        else:
            success = ais_index.create_index(ai_search_resource=self.ai_search_resource,
                               ai_search_apikey=self.ai_search_apikey,
                               search_api_version=self.search_api_version,
                               index_schema_path=self.index_schema,
                               search_index_name=self.search_index_name,
                               vectorize_flag=self.vectorize_flag)
        return success

    def prep_data_source(self):
        """Create data source.
        """
        success = ais_datasrc.create_data_source(ai_search_resource=self.ai_search_resource,
                                        ai_search_apikey=self.ai_search_apikey,
                                        search_api_version=self.search_api_version,
                                        data_src_name=self.data_source_name,
                                        data_src_connstr=self.data_source_conn_str,
                                        data_src_container=self.data_source_container,
                                        data_src_dir=self.data_source_folder)  
        return success

        
    def prep_indexer(self):
        """
        Create Indexer
        """
        success = ais_indexer.create_indexer(ai_search_resource=self.ai_search_resource,
                                        ai_search_apikey=self.ai_search_apikey,
                                        search_api_version=self.search_api_version,
                                        indexer_name= self.search_indexer_name,
                                        indexer_def_path=self.indexer_def,
                                        data_source_name=self.data_source_name,
                                        target_index_name=self.search_index_name,
                                        skillset_name=self.search_skillset_name) 
        return success
    
    def prep_skillset(self):
        """ Create skillset
        """
        success = ais_skillset.create_skillset(ai_search_resource=self.ai_search_resource,
                                        ai_search_apikey=self.ai_search_apikey,
                                        search_api_version=self.search_api_version,
                                        skillset_name=self.search_skillset_name,
                                        skillset_def_path=self.skillset_def,
                                        openai_resource=self.aoai_resource, 
                                        openai_apikey=self.aoai_apikey, 
                                        openai_deploymentid=self.aoai_deploymentid, 
                                        openai_modelname=self.aoai_modelname,
                                        target_index_name=self.search_index_name)
        return success

    def create_search(self):
        """ Main method to create following AI Search components:
        1. Index 2. Data Source 3. Skillset 4. Indexer.
        Note, there is no rollback. 
        """

        log.info('>>> AI SEARCH - creation started.')

        # prepare index definition and create index
        if not self.prep_index():
            log.error('>>> Index is NOT created. AI Search componenets creation is stopped.')
            return False
        
        # prepare data source definition and create data source 
        if not self.prep_data_source():
            log.error('>>> Data Source is NOT created. AI Search componenets creation is stopped.')
            return False

        # prepare skillset definition and create skillset   
        if self.vectorize_flag:
            # vectorization - need vect skillset creaion
            if not self.prep_skillset():
                log.error('>>> Skillset is NOT created. AI Search componenets creation is stopped.')
                return False

        # prepare indexer definition and create indexer  
        if not self.prep_indexer():
            log.error('>>> Indexer is NOT created. AI Search componenets creation is stopped.')
            return False
        
        log.info('>>> AI SEARCH - creation completed OK.')
        return True

if __name__ == '__main__':
    # simple index creation (no vector): crate index, data source, indexer without skills
    # working version
    # base_index_name = 'simple-index'
    # release_name = 'release05'
    # index_schema_path = './data/simple-index/ai_search_index_schema_v1.json'
    # indexer_def_path = './data/simple-index/ai_search_indexer_def_v1.json'
    # skillset_def_path = ''
    # vectorize_flag = False

    # example with vector ind
    base_index_name = 'vect-index'
    release_name = 'release-3oct'
    index_schema_path = './data/vector-index/ai_search_index_schema.json'
    indexer_def_path = './data/vector-index/ai_search_indexer_vector_def_v2.json'
    skillset_def_path = './data/vector-index/ai_search_skillset_vector_def_v2.json'
    vectorize_flag = True

    with open('../config.json', 'r') as f:
        config = json.loads(f.read())

    aisearchops = AISearchOps(config=config, base_index_name=base_index_name, 
                              release_name=release_name,
                              index_schema_path=index_schema_path,
                              indexer_def_path=indexer_def_path,
                              vectorize_flag=vectorize_flag,
                              skillset_def_path=skillset_def_path)
    aisearchops.create_search()
