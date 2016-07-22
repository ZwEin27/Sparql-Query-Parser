# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 19:16:31
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-22 10:26:52


"""
Usage Example

# parse string
python sqparser.py -s "<SPARQL_QUERIES_STRING>"

# parse json file
python sqparser.py -i <INPUT_FILE_PATH> -o <OUTPUT_FILE_PATH> -t <TRUE|FALSE> -c <'WHERE' by default>

# parse sparql-queries.json that contains title, and only extract WHERE component
python sqparser.py -i tests/data/sparql-queries.json -o test.json -t True -c "WHERE"

# parse sparql-queries.json that doesn't contain title, and only extract WHERE component
python sqparser.py -i tests/data/sparql-queries-without-title.json -o test.json -t False -c "WHERE"

"""


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
SQ_KEYWORD_BIND = 'BIND'

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
SQ_EXT_GOL = 'group-by'
SQ_EXT_GROUP_VARIABLE = 'group-variable'
SQ_EXT_ORDER_VARIABLE = 'order-variable'
SQ_EXT_SORTED_ORDER = 'sorted-order'
SQ_EXT_LIMIT = 'limit'

# functions
SQ_FUNCTION_BIND = 'bind'
SQ_FUNCTION_BOUND = 'bound'
SQ_FUNCTION_ASC = 'asc'
SQ_FUNCTION_DESC = 'desc'
SQ_FUNCTION_COUNT = 'count'
SQ_FUNCTION_GROUP_CONCAT = 'group_concat'

SQ_FUNCTIONS = [    # modify SQ_FUNCTION_FUNC also, if update
    SQ_FUNCTION_BIND,
    SQ_FUNCTION_BOUND,
    SQ_FUNCTION_ASC,
    SQ_FUNCTION_DESC,
    SQ_FUNCTION_COUNT,
    SQ_FUNCTION_GROUP_CONCAT
]

######################################################################
#   Regular Expression
######################################################################

re_continues_digits = re.compile(r'\d+')

re_brackets_most_b = re.compile(r'(?<={).*(?=})')
re_brackets_least_b = re.compile(r'(?<={).*?(?=})')
re_brackets_most_m = re.compile(r'(?<=\[).*(?=\])')
re_brackets_least_m = re.compile(r'(?<=\[).*?(?=\])')
re_brackets_most_s = re.compile(r'(?<=\().*(?=\))')
re_brackets_least_s = re.compile(r'(?<=\().*?(?=\))')

re_variable = re.compile(r'(?<=[\(\b\s])\?[\-_a-zA-Z]+(?=[\)\b\s\Z]|$)')

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
re_statement_inner_keyword = re.compile(r'(?:'+r'|'.join(SQ_INNER_KEYWORDS)+r')\s*?[\{\(](?:\(.*?\)|[\s\w!\"#\$%&()\*+\,-\./:;<=>\?@[\]\^_`{|}~])+?[\}\)]')
re_statement_others = re.compile(r'.*?(?=;|\s\.\s?)')
re_statement_a = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[:a-zA-Z])')
# re_statement_a_split = re.compile(r'(?<=[a-zA-Z])\s+?\ba\b\s+?(?=[a-zA-Z])')
re_statement_variable = re.compile(r'(?:^|\s|\b])\?[a-zA-Z]+\b')
re_statement_qpr = re.compile(r'\b(?:(?<=qpr\:)|(?<=\:))\s?[_a-zA-Z]+\b')
re_statement_qpr_constaint = re.compile(r'(?<=\').+(?=\')')
re_statement_content = re.compile(r'(?<=qpr\:).+(?=\s|$)')
# re_statement_content = re.compile(r'qpr\:.+(?=\s|$)')

re_select_variables = re.compile(r'[\{\(](?:\(.*?\)|[\s\w!\"#\$%&()\*+\,-\./:;<=>\?@[\]\^_`{|}~])+?[\}\)]')

# function
# re_function_content = re.compile(r'(?:'+r'|'.join(SQ_FUNCTIONS)+r')'+r'.*', re.IGNORECASE)
def re_functions_content(func_name):
    return re.compile(r'(?<='+func_name+r'\().*?(?=\))', re.IGNORECASE)
re_functions_content = {_:re_functions_content(_) for _ in SQ_FUNCTIONS}
re_function_dependent_variable = re.compile(r'(?<=as)\s+.*(?=\))', re.IGNORECASE)
re_function_distinct = re.compile(r'distinct', re.IGNORECASE)

######################################################################
#   Main Function
######################################################################


class SQParser(object):

    ####################################################
    #   functions for SQ functions
    ####################################################
    def __sqf_func_bind(text):
        # print 'bind'
        # print re_function_content.findall(text)
        pass

    def __sqf_func_bound(text):
        ans = {}
        content = re_functions_content[SQ_FUNCTION_BOUND].search(text)
        if not content:
            raise Exception('Sparql Format Error')
        content = content.group(0).strip()
        ans.setdefault(SQ_FUNCTION_BIND.lower(), content)
        return ans

    def __sqf_func_asc(text):
        pass

    def __sqf_func_desc(text):
        pass

    def __sqf_func_count(text):
        # ?ethnicity  (count(?ad) AS ?count)(group_concat(?ad;separator=',') AS ?ads)
        ans = {}
        ans['variable'] = re_functions_content[SQ_FUNCTION_COUNT].search(text).group(0).strip()
        dependent_variable = re_function_dependent_variable.search(text)
        if dependent_variable:
            ans['dependent-variable'] = dependent_variable.group(0).strip()
        ans['type'] = 'count'
        return ans

    def __sqf_func_group_concat(text):
        ans = {}
        values = re_functions_content[SQ_FUNCTION_GROUP_CONCAT].search(text).group(0).strip()
        ans['distinct'] = False
        if re_function_distinct.search(values):
            ans['distinct'] = True
            values = values.replace('distinct').strip()
        values = values.split(';')
        for value in values:
            if '=' not in value:
                ans['variable'] = value.strip()
            else:
                ov = value.split('=')
                ans[ov[0]] = ov[1][1:-1] if '\'' in ov[1] else ov[1]
        dependent_variable = re_function_dependent_variable.search(text)
        if dependent_variable:
            ans['dependent-variable'] = dependent_variable.group(0).strip()
        ans['type'] = 'group-concat'
        return ans


    SQ_FUNCTIONS_FUNC = {
        SQ_FUNCTION_BIND: __sqf_func_bind,
        SQ_FUNCTION_BOUND: __sqf_func_bound,
        SQ_FUNCTION_ASC: __sqf_func_asc,
        SQ_FUNCTION_DESC: __sqf_func_desc,
        SQ_FUNCTION_COUNT: __sqf_func_count,
        SQ_FUNCTION_GROUP_CONCAT: __sqf_func_group_concat
    }
    
    ####################################################
    #   Outer Component Functions
    ####################################################

    def __cp_func_prefix(parent_ans, text):
        pass

    def __cp_func_select(parent_ans, text):
        # SELECT ?cluster ?ad
        # SELECT ?business  (count(?ad) AS ?count)(group_concat(?ad;separator=',') AS ?ads)
        text = ' '.join(text.strip().split(' ', 1)[1:]) # remove keyword
        ans = {}
        ans['variables'] = []
        variable_fileds = re_select_variables.findall(text)
        for variable_filed in variable_fileds:
            text = text.replace(variable_filed, '').strip()
        variable_fileds += text.split(' ')

        # print variable_fileds
        for variable_filed in variable_fileds:
            # variables in function 
            # print variable_filed
            is_func = False
            for func_name in SQ_FUNCTIONS:
                if func_name in variable_filed:
                    func_rtn = SQParser.SQ_FUNCTIONS_FUNC[func_name](variable_filed)
                    ans['variables'].append(func_rtn)
                    is_func = True
                    break

            if not is_func:
                ans['variables'].append({'variable': variable_filed.strip(), 'type': 'simple'})
            
        

        parent_ans.setdefault(SQ_KEYWORD_SELECT.lower(), ans)

    def __cp_func_where(parent_ans, text):
        ans = {}
        # print '__cp_func_where', text

        statements = [_.strip() for _ in re_statement_inner_keyword.findall(text)]
        # print statements
        for statement in statements:
            text = text.replace(statement, '')
        statements += [_.strip() for _ in re_statement_others.findall(text) if _.strip() != '']
        # print statements
        # statements = re_statement_split.split(text)
        # statements = [_.strip() for _ in re_statement_split.findall(text) if _ != '']
        for statement in statements:
            # print 'statement:', statement.encode('ascii', 'ignore')
            SQParser.parse_statement(ans, statement.strip())
        parent_ans.setdefault(SQ_KEYWORD_WHERE.lower(), ans)
        # return ans
    
    def __cp_func_order(parent_ans, text):
        parent_ans.setdefault(SQ_EXT_GOL, {})
        parent_ans[SQ_EXT_GOL][SQ_EXT_ORDER_VARIABLE] = re_variable.search(text).group(0).strip()

        if re_functions_content[SQ_FUNCTION_ASC].search(text):
            parent_ans[SQ_EXT_GOL][SQ_EXT_SORTED_ORDER] = SQ_FUNCTION_ASC.lower()
        elif re_functions_content[SQ_FUNCTION_DESC].search(text):
            parent_ans[SQ_EXT_GOL][SQ_EXT_SORTED_ORDER] = SQ_FUNCTION_DESC.lower()

    def __cp_func_group(parent_ans, text):
        parent_ans.setdefault(SQ_EXT_GOL, {})
        parent_ans[SQ_EXT_GOL][SQ_EXT_GROUP_VARIABLE] = re_variable.search(text).group(0).strip()

    def __cp_func_limit(parent_ans, text):
        parent_ans.setdefault(SQ_EXT_GOL, {})
        if re_continues_digits.search(text):
            digits = int(re_continues_digits.search(text).group(0).strip())
            if digits > 0:
                parent_ans[SQ_EXT_GOL][SQ_EXT_LIMIT] = digits

    OUTER_COMPONENT_FUNC = {
        SQ_KEYWORD_PREFIX: __cp_func_prefix,
        SQ_KEYWORD_SELECT: __cp_func_select,
        SQ_KEYWORD_WHERE: __cp_func_where,
        SQ_KEYWORD_ORDER: __cp_func_order,
        SQ_KEYWORD_GROUP: __cp_func_group,
        SQ_KEYWORD_LIMIT: __cp_func_limit
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
            
        # content = re_statement_content.search(text).group(0).strip()
        # print component
        return ans

    def __cp_func_optional(text):
        content = re_statement_content.search(text).group(0).strip()
        if not content:
            raise Exception('Sparql Format Error')
        clause = SQParser.parse_content(content)
        clause[SQ_EXT_OPTIONAL_FLAG] = True
        return clause

    def __cp_func_bind(text):
        pass

    INNER_COMPONENT_FUNC = {
        SQ_KEYWORD_FILTER: __cp_func_filter,
        SQ_KEYWORD_OPTIONAL: __cp_func_optional,
        SQ_KEYWORD_BIND: __cp_func_bind
    }

    ####################################################
    #   Main Functions
    ####################################################

    @staticmethod
    def parse_content(text):
        ans = {}
        # text = text.split(' ')
        # print 'parse_content: ', text.strip()
        text = text.strip().split(' ', 1)

        # predicate = re_statement_qpr.search(text).group(0).strip()
        # constraint = re_statement_qpr_constaint.search(text).group(0).strip()
        predicate = text[0]
        constraint = text[1]
        
        constraint = constraint[1:-1] if '\'' in constraint else constraint
        ans[SQ_EXT_PREDICATE] = predicate
        ans.setdefault(SQ_EXT_OPTIONAL_FLAG, False)
        if '?' in constraint:
            ans[SQ_EXT_VARIABLE] = constraint
        else:
            ans[SQ_EXT_CONSTAINT] = constraint
        return ans

    @staticmethod
    def parse_statement(ans, text):
        # print re_statement_a.findall(text)
        if re_statement_a.search(text):
            # print text
            ans[SQ_EXT_TYPE] = re_statement_qpr.search(text).group(0).strip()
            ans[SQ_EXT_VARIABLE] = re_statement_variable.search(text).group(0).strip()
        elif len(re_inner.findall(text)) > 0:
            for component in re_inner.findall(text):
                keyword = re_keyword.match(component).group(0).strip()

                if re_brackets_most_b.search(component):
                    content = re_brackets_most_b.search(component).group(0).strip()
                elif re_brackets_most_s.search(component):
                    content = re_brackets_most_s.search(component).group(0).strip()
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
            # print 'parse_statement:', text
            content = re_statement_content.search(text)
            if not content:
                raise Exception('Sparql Format Error')
            content = content.group(0).strip()
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
        # print text
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
            # print 'key:', key
            # print 'content:', content.encode('ascii', 'ignore')
            # ans[key] = SQParser.OUTER_COMPONENT_FUNC[key](content)
            SQParser.OUTER_COMPONENT_FUNC[key](ans, content)
        return ans

    @staticmethod
    def parse(text, target_component=None):
        components = {re_keyword.match(_).group(0).strip():re_brackets_most_b.search(_).group(0).strip() if re_brackets_most_b.search(_) else _ for _ in re_outer.findall(text)}
        # print components
        
        # if target_component:
        #     t = components[target_component]
        #     print t

        ans = SQParser.parse_components(components)
        if target_component:
            ans = ans[target_component]
        # ans = SQParser.parse_components(components)[target_component]
        # return json.dumps(ans, indent=4)
        return ans

    @staticmethod
    def parse_sq_json(input_path, output_path=None, target_component=None, has_title=True):
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
    # arg_parser.add_argument('-s','--string', required=True)

    # args = arg_parser.parse_args()

    # text = str(args.text)
    # print SQParser.parse(text)
    """

    import sys
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i','--input_file', required=False)
    arg_parser.add_argument('-o','--output_file')
    arg_parser.add_argument('-c','--target_component', required=False)
    arg_parser.add_argument('-t','--has_title', required=False)
    arg_parser.add_argument('-s','--str_input', required=False)

    args = arg_parser.parse_args()

    input_file = str(args.input_file)
    output_file = str(args.output_file)
    target_component = str(args.target_component) if args.target_component else None
    has_title = args.has_title if args.has_title else True
    str_input = args.str_input

    if str_input:
        print json.dumps(SQParser.parse(str_input, target_component=target_component), indent=4)
    else:
        SQParser.parse_sq_json(input_file, output_path=output_file, target_component=target_component, has_title=has_title)

    



