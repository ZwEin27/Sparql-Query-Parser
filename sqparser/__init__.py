# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 19:16:31
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-19 21:30:48

import re

######################################################################
#   Constant
######################################################################

SQ_KEYWORDS = ['SELECT','CONSTRUCT','DESCRIBE','ASK','BASE','PREFIX','LIMIT','OFFSET','DISTINCT','REDUCED','ORDER','BY','ASC','DESC','FROM','NAMED','WHERE','GRAPH','OPTIONAL','UNION','FILTER']

SQ_FUNCTIONS = ['STR','LANGMATCHES','LANG','DATATYPE','BOUND','sameTerm','isIRI','isURI','isBLANK','isLITERAL','REGEX']


######################################################################
#   Regular Expression
######################################################################

re_brackets_most = re.compile(r'\{.*\}')
re_brackets_least = re.compile(r'\{.*?\}')





if __name__ == '__main__':
    print ''
