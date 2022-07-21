import odk


def search_sense_no_test():
    od = odk.OpenDictFetcher()

    print(od.search_sense_no('누리'))
    print(od.search_sense_no('누리', user_content_mode=1))
    print(od.search_sense_no('누리', match=False))
    print(od.search_sense_no('누리', dict_type=2))
