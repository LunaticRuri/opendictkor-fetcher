import odk
from pprint import pprint


def sense_downloader_test():
    od = odk.OpenDictFetcher()

    work_list = [str(i) for i in range(1, 11)]

    pprint(od.sense_downloader(work_list))
    od.sense_downloader(work_list, 'output.json')
