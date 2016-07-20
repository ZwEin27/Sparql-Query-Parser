# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 19:16:31
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-19 23:04:32

import re

######################################################################
#   Constant
######################################################################

SQ_KEYWORD_SELECT = 'SELECT'
SQ_KEYWORD_PREFIX = 'PREFIX'
SQ_KEYWORD_WHERE = 'WHERE'
SQ_KEYWORD_ORDER = 'ORDER'
SQ_KEYWORD_GROUP = 'GROUP'
SQ_KEYWORD_LIMIT = 'LIMIT'
SQ_KEYWORD_FILTER = 'FILTER'
SQ_KEYWORD_OPTIONAL = 'OPTIONAL'


SQ_OUTER_KEYWORDS = ['SELECT','PREFIX','WHERE','ORDER', 'GROUP', 'LIMIT']
SQ_INNER_KEYWORDS = ['FILTER', 'OPTIONAL']

SQ_KEYWORDS = ['SELECT','CONSTRUCT','DESCRIBE','ASK','BASE','PREFIX','LIMIT','OFFSET','DISTINCT','REDUCED','ORDER','BY','ASC','DESC','FROM','NAMED','WHERE','GRAPH','OPTIONAL','UNION','FILTER']

SQ_FUNCTIONS = ['STR','LANGMATCHES','LANG','DATATYPE','BOUND','sameTerm','isIRI','isURI','isBLANK','isLITERAL','REGEX']


######################################################################
#   Regular Expression
######################################################################

re_brackets_most = re.compile(r'(?<={).*(?=})')
re_brackets_least = re.compile(r'(?<={).*?(?=})')

reg_outer = r'(?:'+r'|'.join(SQ_OUTER_KEYWORDS)+r').*?(?='+r'|'.join(SQ_OUTER_KEYWORDS)+r'|\s*$)'
re_outer = re.compile(reg_outer)

# statement
re_statement_split = re.compile(r'[;\.]')
re_statement_a = re.compile(r'(?<=[a-zA-Z])\s*?\ba\b\s*?(?=[a-zA-Z])')
# re_statement_a_split = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[a-zA-Z])')
re_statement_variable = re.compile(r'(?:^|\s])\?[a-zA-Z]+\b')
re_statement_qpr = re.compile(r'\b(?<=qpr\:)[a-zA-Z]+\b')

######################################################################
#   Main Function
######################################################################

class SQParser(object):
    
    def __cp_func_prefix(text):
        pass

    def __cp_func_select(text):
        pass

    # [' ?ad a qpr:Ad ', 
    # " qpr:location 'Fargo, ND' ", 
    # ' qpr:business_type ?bt ', 
    # " FILTER(?bt = 'Spa' || ?bt = 'Massage Parlor') ?ad qpr:services 'sex' ", 
    # ' OPTIONAL { ?ad qpr:business_name ?business_name} OPTIONAL { ?ad qpr:physical_address ?physical_address } BIND( IF(BOUND(?business_name) && BOUND(?physical_address), CONCAT(?business_name, ",", ?physical_address), IF(BOUND(?business_name), ?business_name, ?physical_address)) AS ?business) ']
    def __cp_func_where(text):
        ans = {}
        statements = re_statement_split.split(text)
        for statement in statements:
            SQParser.parse_statement(ans, statement.strip())

        return ans

    COMPONENT_FUNC = {
        SQ_KEYWORD_PREFIX: __cp_func_prefix,
        SQ_KEYWORD_SELECT: __cp_func_select,
        SQ_KEYWORD_WHERE: __cp_func_where,
        SQ_KEYWORD_ORDER: lambda x: None,
        SQ_KEYWORD_GROUP: lambda x: None,
        SQ_KEYWORD_LIMIT: lambda x: None
    }


    @staticmethod
    def parse_statement(ans, text):
        if re_statement_a.search(text):
            # for a
            ans['type'] = re_statement_qpr.findall(text)
            ans['variable'] = re_statement_variable.findall(text)

    @staticmethod
    def parse_components(components):
        ans = {}
        for (key, content) in components.iteritems():
            ans[key] = SQParser.COMPONENT_FUNC[key](content)
        return ans

    @staticmethod
    def parse(text, target_component='WHERE'):
        components = {_.split()[0]:re_brackets_most.search(_).group(0) if re_brackets_most.search(_) else _ for _ in re_outer.findall(text)}
        # print components
        
        # if target_component:
        #     t = components[target_component]
        #     print t

        print SQParser.parse_components(components)[target_component]







if __name__ == '__main__':
    # text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?business  (count(?ad) AS ?count)(group_concat(?ad;separator=',') AS ?ads)   WHERE { ?ad a qpr:Ad ; qpr:location 'Fargo, ND' ; qpr:business_type ?bt . FILTER(?bt = 'Spa' || ?bt = 'Massage Parlor') ?ad qpr:services 'sex' . OPTIONAL { ?ad qpr:business_name ?business_name} OPTIONAL { ?ad qpr:physical_address ?physical_address } BIND( IF(BOUND(?business_name) && BOUND(?physical_address), CONCAT(?business_name, \",\", ?physical_address), IF(BOUND(?business_name), ?business_name, ?physical_address)) AS ?business) } GROUP BY ?business ORDER BY ?count LIMIT 1"
    text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?cluster ?ad WHERE { ?cluster a qpr:cluster ; qpr:seed '5105124396' ; qpr:ad ?ad . OPTIONAL { ?ad qpr:image_with_phone ?iwp } OPTIONAL { ?ad qpr:image_with_email ?iwe } FILTER(bound(?iwp) || bound(?iwe) || ?bt = 'Spa') }"
    SQParser.parse(text)
