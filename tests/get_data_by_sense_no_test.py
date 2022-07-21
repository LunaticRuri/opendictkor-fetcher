import odk


def get_data_by_sense_no_test():
    option_dict = {'hand_no': False}
    od = odk.OpenDictFetcher(option_dict)
    sense_no_list = ['1', '10', '100', '1000', '10000', '100000', '1000000']

    for sn in sense_no_list:
        print(od.get_data_by_sense_no(sn))
        print('\n')
