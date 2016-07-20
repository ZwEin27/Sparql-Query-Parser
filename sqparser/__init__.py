# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 19:16:31
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-20 09:50:10

import re
import json

######################################################################
#   Constant
######################################################################

# keyword
SQ_KEYWORD_SELECT = 'SELECT'
SQ_KEYWORD_PREFIX = 'PREFIX'
SQ_KEYWORD_WHERE = 'WHERE'
SQ_KEYWORD_ORDER = 'ORDER'
SQ_KEYWORD_GROUP = 'GROUP'
SQ_KEYWORD_LIMIT = 'LIMIT'
SQ_KEYWORD_FILTER = 'FILTER'
SQ_KEYWORD_OPTIONAL = 'OPTIONAL'

# operator
SQ_OPERATOR_OR = '||'
SQ_OPERATOR_AND = '&&'

SQ_OUTER_KEYWORDS = ['SELECT','PREFIX','WHERE','ORDER', 'GROUP', 'LIMIT']
SQ_INNER_KEYWORDS = ['FILTER', 'OPTIONAL', 'BIND']

SQ_OUTER_OPERATOR = [SQ_OPERATOR_OR, SQ_OPERATOR_AND]
SQ_INNER_OPERATOR = ['!=', '<=', '>=', '<', '>', '==', '='] # keep in this order

SQ_OPERATOR_MAPPING = {
    SQ_OPERATOR_OR: 'OR',
    SQ_OPERATOR_AND: 'AND'
}

# SQ_KEYWORDS = ['SELECT','CONSTRUCT','DESCRIBE','ASK','BASE','PREFIX','LIMIT','OFFSET','DISTINCT','REDUCED','ORDER','BY','ASC','DESC','FROM','NAMED','WHERE','GRAPH','OPTIONAL','UNION','FILTER']

# SQ_FUNCTIONS = ['STR','LANGMATCHES','LANG','DATATYPE','BOUND','sameTerm','isIRI','isURI','isBLANK','isLITERAL','REGEX']

# extraction names
SQ_EXT_TYPE = 'type'
SQ_EXT_VARIABLE = 'variable'
SQ_EXT_CLAUSES = 'clauses'
SQ_EXT_PREDICATE = 'predicate'
SQ_EXT_CONSTAINT = 'constraint'
SQ_EXT_FILTERS = 'filters'
SQ_EXT_OPTIONAL_FLAG = 'isOptional'
SQ_EXT_OPERATOR = 'operator'

# functions
SQ_FUNCTION_BIND = 'bind'
SQ_FUNCTION_BOUND = 'bound'

SQ_FUNCTIONS = [    # modify SQ_FUNCTION_FUNC also, if update
    SQ_FUNCTION_BIND,
    SQ_FUNCTION_BOUND
]

######################################################################
#   Regular Expression
######################################################################

re_brackets_most_b = re.compile(r'(?<={).*(?=})')
re_brackets_least_b = re.compile(r'(?<={).*?(?=})')
re_brackets_most_m = re.compile(r'(?<=\[).*(?=\])')
re_brackets_least_m = re.compile(r'(?<=\[).*?(?=\])')
re_brackets_most_s = re.compile(r'(?<=\().*(?=\))')
re_brackets_least_s = re.compile(r'(?<=\().*?(?=\))')

# keyword
reg_outer = r'(?:'+r'|'.join(SQ_OUTER_KEYWORDS)+r').*?(?='+r'|'.join(SQ_OUTER_KEYWORDS)+r'|\s*$)'
re_outer = re.compile(reg_outer)
reg_inner = r'(?:'+r'|'.join(SQ_INNER_KEYWORDS)+r').*?(?='+r'|'.join(SQ_INNER_KEYWORDS)+r'|\s*$)'
re_inner = re.compile(reg_inner)

re_keyword = re.compile(r'^[a-zA-Z]+\b')

# operator 
reg_outer_operator = r'(?:'+r'|'.join(SQ_OUTER_OPERATOR)+r').*?(?='+r'|'.join(SQ_OUTER_OPERATOR)+r'|\s*$)'
re_outer_operator = re.compile(reg_outer_operator)
re_outer_operator_split = re.compile(r'['+r''.join(SQ_OUTER_OPERATOR)+r']')
reg_inner_operator = r'(?:'+r'|'.join(SQ_INNER_OPERATOR)+r').*?(?='+r'|'.join(SQ_INNER_OPERATOR)+r'|\s*$)'
re_inner_operator = re.compile(reg_inner_operator)


# statement
# re_statement_split = re.compile(r'[;\.]')
re_statement_split = re.compile(r'.*?(?=;|\s\.\s)')
re_statement_a = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[:a-zA-Z])')
# re_statement_a_split = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[a-zA-Z])')
re_statement_variable = re.compile(r'(?:^|\s])\?[a-zA-Z]+\b')
re_statement_qpr = re.compile(r'\b(?:(?<=qpr\:)|\b(?<=\:))[a-zA-Z]+\b')
re_statement_content = re.compile(r'(?<=qpr\:).+(?=\s|$)')


# function
re_function_content = re.compile(r'(?:'+r'|'.join(SQ_FUNCTIONS)+r')'+r'.*', re.IGNORECASE)
def re_functions_content(func_name):
    return re.compile(r'(?<='+func_name+r'\().*?(?=\))')
re_functions_content = {_:re_functions_content(_) for _ in SQ_FUNCTIONS}


######################################################################
#   Main Function
######################################################################


class SQParser(object):

    ####################################################
    #   functions for SQ functions
    ####################################################
    def __sqf_func_bind(text):
        print 'bind'
        print re_function_content.findall(text)

    def __sqf_func_bound(text):
        ans = {}
        content = re_functions_content[SQ_FUNCTION_BOUND].search(text)
        if not content:
            raise Exception('Sparql Format Error')
        content = content.group(0)
        ans.setdefault(SQ_FUNCTION_BIND.lower(), content)
        return ans

        

    SQ_FUNCTIONS_FUNC = {
        SQ_FUNCTION_BIND: __sqf_func_bind,
        SQ_FUNCTION_BOUND: __sqf_func_bound
    }
    
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
        statements = [_.strip() for _ in re_statement_split.findall(text) if _ != '']
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
        # print text
        ans = {}
        for op in SQ_OUTER_OPERATOR:
            if op in text:
                ans.setdefault(SQ_EXT_OPERATOR, [])
                ans[SQ_EXT_OPERATOR].append(op)

        component = [_.strip() for _ in re_outer_operator_split.split(text) if _ != '']

        subc_rtn = SQParser.parse_subcomponents(component)
        if len(subc_rtn) > 0:
            ans.setdefault(SQ_EXT_CLAUSES, [])
            ans[SQ_EXT_CLAUSES] += subc_rtn
            
        # content = re_statement_content.search(text).group(0)
        print component
        return ans

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
        text = text.split(' ')
        print 'parse_content: ', text
        cv = text[1]
        ans[SQ_EXT_PREDICATE] = text[0]
        if '?' in cv:
            ans[SQ_EXT_VARIABLE] = cv
        else:
            ans[SQ_EXT_CONSTAINT] = cv
        return ans

    @staticmethod
    def parse_statement(ans, text):
        # print re_statement_a.findall(text)
        if re_statement_a.search(text):
            print text
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

                icf_rtn = SQParser.INNER_COMPONENT_FUNC[keyword](content)
                if keyword == SQ_KEYWORD_OPTIONAL:
                    ans.setdefault(SQ_EXT_CLAUSES, [])
                    ans[SQ_EXT_CLAUSES].append(icf_rtn)
                elif keyword == SQ_KEYWORD_FILTER:
                    ans.setdefault(SQ_EXT_FILTERS, [])
                    ans[SQ_EXT_FILTERS].append(icf_rtn)
        else:
            print 'parse_statement', text
            content = re_statement_content.search(text)
            if not content:
                raise Exception('Sparql Format Error')
            content = content.group(0)
            ans.setdefault(SQ_EXT_CLAUSES, [])
            ans[SQ_EXT_CLAUSES].append(SQParser.parse_content(content))

    @staticmethod
    def parse_inner_operator(text):
        ans = {}
        items = text.strip().split(' ')
        ans.setdefault(SQ_EXT_VARIABLE, items[0])
        ans.setdefault(SQ_EXT_OPERATOR, items[1])
        ans.setdefault(SQ_EXT_CONSTAINT, items[2])
        return ans

    @staticmethod
    def parse_subcomponent(text):
        # functions or condition statement
        
        # handle functions
        for func_name in SQ_FUNCTIONS:
            if func_name in text:
                return SQParser.SQ_FUNCTIONS_FUNC[func_name](text)

        # else handle conditions
        for op_name in SQ_INNER_OPERATOR:
            if op_name in text:
                return SQParser.parse_inner_operator(text)

        raise Exception('Sparql Format Error')
         


    @staticmethod
    def parse_subcomponents(subcomponents):
        ans = []
        for subcomponent in subcomponents:
            ans.append(SQParser.parse_subcomponent(subcomponent))
        return ans


    @staticmethod
    def parse_components(components):
        ans = {}
        for (key, content) in components.iteritems():
            ans[key] = SQParser.OUTER_COMPONENT_FUNC[key](content)
        return ans

    @staticmethod
    def parse(text, target_component='WHERE'):
        components = {re_keyword.match(_).group(0):re_brackets_most_b.search(_).group(0) if re_brackets_most_b.search(_) else _ for _ in re_outer.findall(text)}
        # print components
        
        # if target_component:
        #     t = components[target_component]
        #     print t

        ans = SQParser.parse_components(components)[target_component]
        # return json.dumps(ans, indent=4)
        return ans

    @staticmethod
    def parse_sq_json(input_path, output_path=None, target_component='WHERE', has_title=True):
        with open(input_path, 'rb') as file_handler:
            # lines = file_handler.readlines()
            json_obj = json.load(file_handler)
            # contents = []
            # if has_title: 
            #     for value in json_obj.values():
            #         for (k, v) in value.iteritems():
            #             contents.append(v['sparql'])
            # else:
            #     for (k, v) in json_obj.iteritems():
            #         contents.append(v['sparql'])
            
            if has_title: 
                for value in json_obj.values():
                    for (k, v) in value.iteritems():
                        value[k]['parsed'] = SQParser.parse(v['sparql'], target_component=target_component)
            else:
                for (k, v) in json_obj.iteritems():
                    k['parsed'] = SQParser.parse(v['sparql'], target_component=target_component)

        # for content in contents:
        #     SQParser.parse(content, target_component=target_component)

        if output_path:
            file_handler = open(output_path, 'wb')
            file_handler.write(json.dumps(json_obj, sort_keys=True, indent=4))
            file_handler.close()







if __name__ == '__main__':

    """
    text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?cluster ?ad WHERE { ?cluster a qpr:cluster ; qpr:seed '5105124396' ; qpr:ad ?ad . OPTIONAL { ?ad qpr:image_with_phone ?iwp } OPTIONAL { ?ad qpr:image_with_email ?iwe } FILTER(bound(?iwp) || bound(?iwe) || ?bt = 'Spa') }"
    
    SQParser.parse(text)
    

    # import sys
    # import argparse

    # arg_parser = argparse.ArgumentParser()
    # arg_parser.add_argument('-t','--text', required=True)

    # args = arg_parser.parse_args()

    # text = str(args.text)
    # print SQParser.parse(text)
    """

    import sys
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i','--input_file', required=True)
    arg_parser.add_argument('-o','--output_file')
    arg_parser.add_argument('-c','--target_component', required=False)
    arg_parser.add_argument('-t','--has_title', required=False)

    args = arg_parser.parse_args()

    input_file = str(args.input_file)
    output_file = str(args.output_file)
    target_component = str(args.target_component)
    has_title = args.has_title if args.has_title else False
    SQParser.parse_sq_json(input_file, output_path=output_file, target_component=target_component, has_title=has_title)

    



