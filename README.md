# Azure AI Search Ops

## Description
This project could be used to automate Azure AI Search configuration as part of CI/CD pipeline. Currently with bicep you can create resource only, however indexes, data sources, indexers etc are not created in bicep. 
Thus essentially CI/CD for Azure AI Search is a 2 step process:
1. Bicep (or any other way) - create resource (this typically is done only once).
2. Separate Script to create internal components of Azure AI Search (index, indexer, skillset, data source etc).
Second step could be done in multiple ways like calling directly service REST endpoints OR via using SDKs available. 
Separate script could be deployed as Azure Function which will essentially will create all the components of the search. 
This is implementation works for the PULL strategy (AI Search). Vectorization is done as part of skillset. 

Data is located in the data source, there is indexer which indexes it into created index.

You can modify the code to add as many data sources as needed and respectively ingest the data into as many indexes as needed. 
More info about data source, indexer and index relationships could be found here. 

https://learn.microsoft.com/en-us/azure/search/search-indexer-overview 

## Code
There are 2 ways to use this code.
1. Folder "indexing-ops" contains all classes implementing creation of index, data source, indexer, skillset etc. And could be invoked as is.
2. Folder "function" could be used for deploying this code as Azure Function which could be triggered when needed.
Before executing the code, make sure to update definition files as needed. Located in "data" folder. 
3. To execute create of all components use ai_search_ops.py

## Execution Notes
1. If creation of components is not successful - there is no roll back. This should be implemented separately.
2. If you need more than 1 data source - you'll need to modify main components creation flow to create 2 data sources and 2 indexers pointing to the same or different indexes.
3. Azure Key Vault recommended to store access keys.
4. Before executing locally create "config.json" based on the shared template file. 

## Examples
Repo supports creation of simple index (use templates from data/simple-index) and vector index.

## License
This project is licensed under the MIT License.

## Contact
- Email: example@example.com

