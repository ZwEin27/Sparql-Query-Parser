# Sparql-Query-Parser
a pure python utility to parse sparql query into json format


## Command Line Example Usuage

parse string

    python sqparser.py -s "<SPARQL_QUERIES_STRING>"

parse json file

    python sqparser.py -i <INPUT_FILE_PATH> -o <OUTPUT_FILE_PATH> -t <TRUE|FALSE> -c <SPECIFIC_KEY_NAME>

## Python Example Usuage


parse string
    
    text = 'PREFIX qpr: <http://istresearch.com/qpr> SELECT ?number_of_individuals (count(?ad) AS ?count)(group_concat(?ad;separator=',') AS ?ads) WHERE { ?ad a qpr:Ad ; qpr:location 'Eugene, OR' ; qpr:number_of_individuals ?number_of_individuals .  } GROUP BY ?number_of_individuals ORDER BY DESC(?count) LIMIT 1'
    
    SQParser.parse(text)

    # output shown below

    {
        "group-by": {
            "sorted-order": "desc", 
            "limit": 1, 
            "group-variable": "?number_of_individuals", 
            "order-variable": "?count"
        }, 
        "where": {
            "variable": "?ad", 
            "clauses": [
                {
                    "predicate": "location", 
                    "isOptional": false, 
                    "constraint": "Eugene, OR"
                }
            ], 
            "type": "Ad"
        }, 
        "select": {
            "variables": [
                {
                    "variable": "?ad", 
                    "dependent-variable": "?count", 
                    "type": "count"
                }, 
                {
                    "distinct": false, 
                    "variable": "?ad", 
                    "dependent-variable": "?ads", 
                    "separator": ",", 
                    "type": "group-concat"
                }, 
                {
                    "variable": "?number_of_individuals", 
                    "type": "simple"
                }
            ]
        }
    }

parse json file
    
    input_file = <INPUT_FILE_PATH>
    output_path = <OUTPUT_FILE_PATH>
    target_component = <DEFAULT: NONE, OPTIONS: where, select...>
    has_title = <True|False, True by default>

    SQParser.parse_sq_json(input_file, output_path=output_file, target_component=target_component, has_title=has_title)
