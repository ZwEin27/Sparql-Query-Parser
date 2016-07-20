# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 19:16:31
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-20 00:19:16

import re
import json

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


SQ_EXT_TYPE = 'type'
SQ_EXT_VARIABLE = 'variable'
SQ_EXT_CLAUSES = 'clauses'
SQ_EXT_PREDICATE = 'predicate'
SQ_EXT_CONSTAINT = 'constraint'
SQ_EXT_FILTERS = 'filters'
SQ_EXT_OPTIONAL_FLAG = 'isOptional'

######################################################################
#   Regular Expression
######################################################################

re_brackets_most_b = re.compile(r'(?<={).*(?=})')
re_brackets_least_b = re.compile(r'(?<={).*?(?=})')
re_brackets_most_m = re.compile(r'(?<=\[).*(?=\])')
re_brackets_least_m = re.compile(r'(?<=\[).*?(?=\])')
re_brackets_most_s = re.compile(r'(?<=\().*(?=\))')
re_brackets_least_s = re.compile(r'(?<=\().*?(?=\))')

reg_outer = r'(?:'+r'|'.join(SQ_OUTER_KEYWORDS)+r').*?(?='+r'|'.join(SQ_OUTER_KEYWORDS)+r'|\s*$)'
re_outer = re.compile(reg_outer)
reg_inner = r'(?:'+r'|'.join(SQ_INNER_KEYWORDS)+r').*?(?='+r'|'.join(SQ_INNER_KEYWORDS)+r'|\s*$)'
re_inner = re.compile(reg_inner)

re_keyword = re.compile(r'^[a-zA-Z]+\b')

# statement
re_statement_split = re.compile(r'[;\.]')
re_statement_a = re.compile(r'(?<=[a-zA-Z])\s*?\ba\b\s*?(?=[a-zA-Z])')
# re_statement_a_split = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[a-zA-Z])')
re_statement_variable = re.compile(r'(?:^|\s])\?[a-zA-Z]+\b')
re_statement_qpr = re.compile(r'\b(?<=qpr\:)[a-zA-Z]+\b')
re_statement_content = re.compile(r'(?<=qpr\:).+(?=\s|$)')

######################################################################
#   Main Function
######################################################################

class SQParser(object):
    
    ####################################################
    #   Outer Component Functions
    ####################################################

    def __cp_func_prefix(text):
        pass

    def __cp_func_select(text):
        pass

    def __cp_func_where(text):
        ans = {}
        statements = re_statement_split.split(text)
        for statement in statements:
            SQParser.parse_statement(ans, statement.strip())

        return ans

    OUTER_COMPONENT_FUNC = {
        SQ_KEYWORD_PREFIX: __cp_func_prefix,
        SQ_KEYWORD_SELECT: __cp_func_select,
        SQ_KEYWORD_WHERE: __cp_func_where,
        SQ_KEYWORD_ORDER: lambda x: None,
        SQ_KEYWORD_GROUP: lambda x: None,
        SQ_KEYWORD_LIMIT: lambda x: None
    }

    ####################################################
    #   Inner Component Functions
    ####################################################

    def __cp_func_filter(text):
        return 's'

    def __cp_func_optional(text):
        content = re_statement_content.search(text).group(0)
        if not content:
            raise Exception('Sparql Format Error')
        clause = SQParser.parse_content(content)
        clause[SQ_EXT_OPTIONAL_FLAG] = True
        return clause

    INNER_COMPONENT_FUNC = {
        SQ_KEYWORD_FILTER: __cp_func_filter,
        SQ_KEYWORD_OPTIONAL: __cp_func_optional
    }

    ####################################################
    #   Main Functions
    ####################################################

    @staticmethod
    def parse_content(text):
        ans = {}
        # content = content.group(0).split(' ')
        text = text.split(' ')
        cv = text[1]
        ans[SQ_EXT_PREDICATE] = text[0]
        if '?' in cv:
            ans[SQ_EXT_VARIABLE] = cv
        else:
            ans[SQ_EXT_CONSTAINT] = cv
        return ans



    @staticmethod
    def parse_statement(ans, text):
        if re_statement_a.search(text):
            ans[SQ_EXT_TYPE] = re_statement_qpr.search(text).group(0)
            ans[SQ_EXT_VARIABLE] = re_statement_variable.search(text).group(0)
        elif len(re_inner.findall(text)) > 0:
            for component in re_inner.findall(text):
                keyword = re_keyword.match(component).group(0)

                if re_brackets_most_b.search(component):
                    content = re_brackets_most_b.search(component).group(0)
                elif re_brackets_most_s.search(component):
                    content = re_brackets_most_s.search(component).group(0)
                else:
                    content = component

                ans[SQ_EXT_CLAUSES].append(SQParser.INNER_COMPONENT_FUNC[keyword](content))
        else:
            content = re_statement_content.search(text)
            if not content:
                raise Exception('Sparql Format Error')
            content = content.group(0)
            ans.setdefault(SQ_EXT_CLAUSES, [])
            ans[SQ_EXT_CLAUSES].append(SQParser.parse_content(content))


    @staticmethod
    def parse_components(components):
        ans = {}
        for (key, content) in components.iteritems():
            ans[key] = SQParser.OUTER_COMPONENT_FUNC[key](content)
        return ans

    @staticmethod
    def parse(text, target_component='WHERE'):
        components = {_.split()[0]:re_brackets_most_b.search(_).group(0) if re_brackets_most_b.search(_) else _ for _ in re_outer.findall(text)}
        # print components
        
        # if target_component:
        #     t = components[target_component]
        #     print t

        ans = SQParser.parse_components(components)[target_component]
        print json.dumps(ans, indent=4)







if __name__ == '__main__':
    # """
    text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?cluster ?ad WHERE { ?cluster a qpr:cluster ; qpr:seed '5105124396' ; qpr:ad ?ad . OPTIONAL { ?ad qpr:image_with_phone ?iwp } OPTIONAL { ?ad qpr:image_with_email ?iwe } FILTER(bound(?iwp) || bound(?iwe) || ?bt = 'Spa') }"
    
    SQParser.parse(text)
    """

    import sys
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-t','--text', required=True)

    args = arg_parser.parse_args()

    text = str(args.text)
    print SQParser.parse(text)

    """



