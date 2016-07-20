# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-07-19 14:48:56
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-07-19 22:06:50


import re

# text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?review_site  (count(?ad) AS ?count)(group_concat(?ad;separator=',') AS ?ads) WHERE { ?ad a qpr:Ad ; qpr:location 'Capetown, South Africa' ; qpr:review_site ?review_site . } GROUP BY ?review_site ORDER BY DESC(?count) LIMIT 1"

# text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?cluster ?ad WHERE {    ?cluster a qpr:cluster ; qpr:seed '5105124396' . qpr:ad ?ad . OPTIONAL { ?ad qpr:image_with_phone ?iwp } OPTIONAL { ?ad qpr:image_with_email ?iwe } FILTER(bound(?iwp) || bound(?iwe)) }"
 
text = "PREFIX qpr: <http://istresearch.com/qpr> SELECT ?cluster ?ad WHERE  {    ?cluster a qpr:cluster ;              qpr:seed '5105124396' ;              qpr:ad ?ad .      OPTIONAL { ?ad qpr:image_with_phone ?iwp }       OPTIONAL { ?ad qpr:image_with_email ?iwe } } FILTER(bound(?iwp) || bound(?iwe) || ?bt = 'Spa') "

re_ = re.compile(r'(?<={).*(?=})')

# re_s = re.compile(r'.*?(?=;)')

a = ' '.join(re_.findall(text)) 
print a
b = re.split(r'[\.;]', a)
# print b

# re_optional = re.compile(r'(OPTIONAL\s+\{.*?\}\s+)+')
re_optional = re.compile(r'((?<=OPTIONAL)\s+\{.+?\s+\})')
c = re_optional.findall(text)

# print re.findall(r'\{.*\}', text)

SQ_KEYWORDS = ['SELECT','PREFIX','WHERE','ORDER BY', 'GROUP BY', 'LIMIT']
reg_kw = r'(?:'+r'|'.join(SQ_KEYWORDS)+r').*?(?='+r'|'.join(SQ_KEYWORDS)+r'|\s*$)'
re_kw = re.compile(reg_kw)
# print re_kw.findall(text)




