import unittest
import warnings
from datetime import datetime

import nohrsc

class TestNOHRSC(unittest.TestCase):

    # def setUp(self):
    #     args = ['-d', '2019-12-06-15', '-p', '6', '-t', 'nc']
    #
    #     parser = nohrsc.create_arg_parser()
    #     args = parser.parse_args(args)

    ############################################################################
    ########################## Test adjust_date ################################
    ############################################################################

    def test_adjust_date_1(self):
        args_in = ['-d', '2019-12-06-18', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-18', date_adjusted)



    def test_adjust_date_2(self):
        args_in = ['-d', '2019-12-06-15', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_3(self):
        args_in = ['-d', '2019-12-06-00', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-00', date_adjusted)



    def test_adjust_date_4(self):
        args_in = ['-d', '2019-12-06-06', '-p', '24', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-00', date_adjusted)



    def test_adjust_date_5(self):
        args_in = ['-d', '2019-12-06-13', '-p', '24', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_6(self):
        args_in = ['-d', '2019-12-06-13', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-06-12', date_adjusted)



    def test_adjust_date_7(self):
        args_in = ['-d', '2019-12-06-04', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        date_adjusted = nohrsc.adjust_date(args)
        date_adjusted = datetime.strftime(date_adjusted, '%Y-%m-%d-%H')
        self.assertEqual('2019-12-05-12', date_adjusted)




    ############################################################################
    ########################## Test parse_fname ################################
    ############################################################################



    def test_parse_fname_1(self):
        args_in = ['-d', '2019-12-06-18', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_6h_2019120618.nc'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_2(self):
        args_in = ['-d', '2019-12-06-21', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_6h_2019120618.nc'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_3(self):
        args_in = ['-d', '2019-12-06-00', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_6h_2019120600.nc'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_4(self):
        args_in = ['-d', '2019-12-06-21', '-p', '6', '-t', 'tif']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_6h_2019120618.tif'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_5(self):
        args_in = ['-d', '2019-12-15-21', '-p', '24', '-t', 'tif']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_24h_2019121512.tif'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_6(self):
        args_in = ['-d', '2019-12-15-21', '-p', '48', '-t', 'tif']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_48h_2019121512.tif'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_7(self):
        args_in = ['-d', '2019-12-15-21', '-p', '72', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_72h_2019121512.nc'

        self.assertEqual(f_name, f_name_actual)


    # Seasonal accum filenames
    def test_parse_fname_8(self):
        args_in = ['-d', '2019-12-15-21', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_2019093012_to_2019121512.nc'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_9(self):
        args_in = ['-d', '2018-12-15-18', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_2018093012_to_2018121512.nc'

        self.assertEqual(f_name, f_name_actual)



    def test_parse_fname_10(self):
        args_in = ['-d', '2019-12-15-06', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        f_name = nohrsc.parse_fname(args)
        f_name_actual = 'sfav2_CONUS_2019093012_to_2019121412.nc'

        self.assertEqual(f_name, f_name_actual)



    ############################################################################
    ########################### Test parse_url #################################
    ############################################################################



    def test_parse_url_1(self):
        args_in = ['-d', '2019-12-15-18', '-p', '6', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        url = nohrsc.parse_url(args)
        url_actual = 'https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_6h_2019121518.nc'

        self.assertEqual(url, url_actual)



    def test_parse_url_2(self):
        args_in = ['-d', '2019-12-15-18', '-p', '24', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        url = nohrsc.parse_url(args)
        url_actual = 'https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_24h_2019121512.nc'

        self.assertEqual(url, url_actual)



    def test_parse_url_3(self):
        args_in = ['-d', '2019-12-15-18', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        url = nohrsc.parse_url(args)
        url_actual = 'https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_2019093012_to_2019121512.nc'

        self.assertEqual(url, url_actual)



    def test_parse_url_4(self):
        args_in = ['-d', '2019-12-15-06', '-p', '99', '-t', 'nc']

        parser = nohrsc.create_arg_parser()
        args = parser.parse_args(args_in)

        url = nohrsc.parse_url(args)
        url_actual = 'https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_2019093012_to_2019121412.nc'

        self.assertEqual(url, url_actual)




if __name__ == '__main__':
    unittest.main()
