# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-11-21 16:27:32
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-21 16:40:35

import os
import sys
import json


def generate_html_files(input_path, output_path):

    ans = []
    with open(input_path, 'r') as file_handler:
        for line in file_handler:
            json_obj = json.loads(line)
            ans.append(json_obj['raw_content'])

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    for i, json_obj in enumerate(ans):
        with open(os.path.join(output_path, str(i)+'.html'), 'w') as file_handler:
            file_handler.write(json.dumps(json_obj)[1:-1])
            # file_handler.write(json_obj)





    
        


if __name__ == '__main__':
    input_path = os.path.join(os.path.dirname(__file__), '25.jl')
    output_path = os.path.join(os.path.dirname(__file__), 'html')
    generate_html_files(input_path, output_path)
