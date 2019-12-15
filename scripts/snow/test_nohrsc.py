import unittest
import warnings
from datetime import datetime

import nohrsc

class TestNOHRSC(unittest.TestCase):

    # def setUp(self):
    #     args = ['-d', '2019-12-06-15', '-p', '6', '-t', 'nc']
    #
    #     parser = nohrsc.create_arg_parser()
    #     self.args = parser.parse_args(args)

    ############################################################################
    ########################## Test adjust_date ################################
    ############################################################################

    def test_adjust_date_1(self):
        args = ['-d', '2019-12-06-18', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-18', date_adjusted)



    def test_adjust_date_2(self):
        args = ['-d', '2019-12-06-15', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_3(self):
        args = ['-d', '2019-12-06-00', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-00', date_adjusted)



    def test_adjust_date_4(self):
        args = ['-d', '2019-12-06-06', '-p', '24', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-00', date_adjusted)



    def test_adjust_date_5(self):
        args = ['-d', '2019-12-06-13', '-p', '24', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_6(self):
        args = ['-d', '2019-12-06-13', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_7(self):
        args = ['-d', '2019-12-06-04', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        self.args = parser.parse_args(args)

        date_adjusted = nohrsc.adjust_date(self.args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-05-12', date_adjusted)




    ############################################################################
    ########################## Test adjust_date ################################
    ############################################################################


if __name__ == '__main__':
    unittest.main()
