"""
Author: Matt Nicholson

Functions to retrieve and parse RSS products from the National Hurricane Center
"""
import feedparser
import requests
import re
import argparse
import xml.etree.ElementTree as ET


def loadRSS(url, fname):

    # creating HTTP response object from given url
    resp = requests.get(url)

    # saving the xml file
    with open(fname, 'wb') as f:
        f.write(resp.content)

    return fname



def scrub_tags(dirty_str):
    cleaner = re.compile('<.*?>')
    clean_text = re.sub(cleaner, '', dirty_str)
    return clean_text



def parseXML(xmlfile):

    # create element tree object
    tree = ET.parse(xmlfile)

    # get root element
    root = tree.getroot()

    # create empty list for news items
    newsitems = []

    # iterate news items
    for item in root.findall('./channel/item'):

        # empty news dictionary
        news = {}

        # iterate child elements of item
        for child in item:

            # special checking for namespace object content:media
            if child.tag == '{http://search.yahoo.com/mrss/}content':
                news['media'] = child.attrib['url']
            else:
                news[child.tag] = child.text.encode('utf8')

        # append news dictionary to news items list
        newsitems.append(news)

    # return news items list
    return newsitems



def init_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", "--storm_num", nargs='?', const=0,
            help="Storm number of the current tropical Atlantic Season")

    parser.add_argument("-w", "--write", action="store_true", help="Write output to file")
    parser.add_argument("-a", "--address", help="Recipient email address")

    args = parser.parse_args()

    return args



def main():

    args = init_argparser()
    storm_num = args.storm_num

    urls = {'outlook_atl': 'https://www.nhc.noaa.gov/xml/TWOAT.xml',
            'pubadv_atl' : 'https://www.nhc.noaa.gov/xml/TCPAT{}.xml'.format(storm_num),
            'fcstadv_atl': 'https://www.nhc.noaa.gov/xml/TCMAT{}.xml'.format(storm_num),
            'fsctdisc_atl': 'https://www.nhc.noaa.gov/xml/TCDAT{}.xml'.format(storm_num)
    }

    for key, url in urls.items():
        fname = 'nhc_rss_samp-{}.xml'.format(key)
        news = ''

        loadRSS(url, fname)

        try:
            news = parseXML(fname)
        except:
            pass

        for x in news:

            curr_title = scrub_tags(x['title'].decode('UTF-8'))
            curr_desc = scrub_tags(x['description'].decode('UTF-8'))

            if ((key == 'fcstadv_atl') and (len(curr_title) > 100)):
                curr_title = ''

            if (args.write):
                f_txt = fname[:-3] + 'txt'
                with open(f_txt, 'w') as f:
                    f.write(curr_title)
                    f.write(curr_desc)

            if (args.address):
                print(curr_title)
                print(curr_desc)




if __name__ == '__main__':
    main()
