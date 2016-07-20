import sys
import time
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

input_ = os.path.expanduser(os.path.join(TEST_DATA_DIR, 'sparql-queries.json'))
output_ = os.path.expanduser(os.path.join(TEST_DATA_DIR, 'parsed-sparql-queries.json'))


from sqparser import SQParser

class TestSQParserMethods(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parser(self):
        target_component = 'WHERE'
        has_title = True
        SQParser.parse_sq_json(input_, output_path=output_, target_component=target_component, has_title=has_title)

    

if __name__ == '__main__':
    # unittest.main()

    def run_main_test():
        suite = unittest.TestSuite()
        suite.addTest(TestSQParserMethods('test_parser'))
        runner = unittest.TextTestRunner()
        runner.run(suite)

    run_main_test()



