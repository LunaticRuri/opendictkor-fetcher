import requests
import re
import json
import time
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class OpenDictFetcher:
    ALL = 0
    EXPERT_ONLY = 1
    USER_ONLY = 2

    VOCABULARY = 1
    IDIOM = 2
    DEFINITION = 3
    USAGE = 4

    SUCCESS = 0
    BLANK_ERR = 1
    NETWORK_ERR = 2

    dictionary_url = "https://opendict.korean.go.kr/dictionary/view?sense_no="
    search_url = "https://opendict.korean.go.kr/search/searchResult?"

    DEFAULT_REQUEST_DATA = {
        'sense_no': True,
        'word': True,
        'word_hyphen': True,
        'word_no': True,
        'org': True,
        'org_part': True,
        'sound': True,
        'sound_url': True,
        'conj_form': True,
        'class': True,
        'field': True,
        'pos': True,
        'pattern': True,
        'sci_name': True,
        'hg_word_no': True,
        'def': True,
        'ex': True,
        'hand_no': True,
        'related': True,
    }

    def __init__(self, request_data=None):
        """
        :param request_data: 어떤 데이터를 가져올 것인지 dictionary 형태로 초기에 지정할 수 있음
        """

        # request_data 유효성 검증
        if request_data is None:
            self.request_data = OpenDictFetcher.DEFAULT_REQUEST_DATA
        else:
            for k in request_data.keys():
                if k not in OpenDictFetcher.DEFAULT_REQUEST_DATA:
                    raise Exception('Wrong request_data')
            for k, v in OpenDictFetcher.DEFAULT_REQUEST_DATA.items():
                if k not in request_data:
                    request_data[k] = v
            self.request_data = request_data

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @staticmethod
    def get_soup_by_url(url):
        try:
            r = requests.get(url, verify=False, timeout=20)
        except Exception as e:
            err_msg = f'Network ERR: {e}'
            # print(err_msg)
            return False
        else:
            soup = BeautifulSoup(r.text, "lxml")
            # optional - 차단 가능성 있음!!
            time.sleep(0.1)
            return soup

    def search_sense_no(self, query_str, dict_type=1, match=True, user_content_mode=0):
        """
        우리말샘 사전 검색 결과에서 sense_no를 가져옴
        :param query_str: 검색 문자열
        :param dict_type: 1 - 어휘, 2 - 속담/관용구, 3 - 뜻풀이, 4 - 용례 (우리말샘 검색 기준), default=1
        :param match: True - 완전히 일치, False - 일부 일치, default=True
        :param user_content_mode: 0 - 전문가 감수 + 참여자 제안, 1 - 전문가 감수, 2 - 참여자 제안, default=0
        :return: 성공시 검색 결과인 sense_no의 리스트, 실패시 False
        """

        if user_content_mode == OpenDictFetcher.ALL:
            return self.search_sense_no(query_str, dict_type, match, OpenDictFetcher.EXPERT_ONLY) + \
                   self.search_sense_no(query_str, dict_type, match, OpenDictFetcher.USER_ONLY)
        elif user_content_mode == OpenDictFetcher.EXPERT_ONLY:
            content_attr = "&infoType=confirm"
        elif user_content_mode == OpenDictFetcher.USER_ONLY:
            content_attr = "&infoType=suggest"
        else:
            raise Exception('Check content_attr')

        wm = '&wordMatch=Y' if match and dict_type == OpenDictFetcher.VOCABULARY else ''
        query_url = OpenDictFetcher.search_url + f"query={query_str}&dicType={dict_type}{wm}&currentPage=1&rowsperPage=50" + content_attr

        soup = OpenDictFetcher.get_soup_by_url(query_url)
        if not soup:
            print(f'where query_str: {query_str}')
            return False

        try:
            max_page = int(soup.find('div', {'class': 'paging_area'}).text[:-2].split('\n')[-1])
        except AttributeError:
            max_page = 0

        if max_page == 0:
            return []

        sense_no_list = []
        for page in range(1, max_page + 1):
            query_url = OpenDictFetcher.search_url + \
                        f"query={query_str}&dicType={dict_type}{wm}&currentPage={page}&rowsperPage=50" + content_attr
            soup = OpenDictFetcher.get_soup_by_url(query_url)
            if not soup:
                print(f'where sense_no: {query_str}')
                return False

            try:
                search_result = soup.find('div', {'class': 'search_result'}).find_all('a')
                sense_no_list.extend([re.findall(r"\d+", elem.attrs['href'])[0] for elem in search_result])
            except AttributeError:
                sense_no_list = []

        return sense_no_list

    def get_data_by_sense_no(self, sense_no):
        """
        sense_no로 해당 단어 데이터 가져옴. 데이터 명세는 readme 파일과 OpenDictFetcher.DEFAULT_REQUEST_DATA 참고.
        :param sense_no: sense_no - word_no랑 다름!
        :return: 성공시 가져온 데이터를 담은 dictionary 반환, 실패시 False
        """

        output_dict = dict()

        if not type('') == type(sense_no):
            sense_no = str(sense_no)
        if self.request_data['sense_no']:
            output_dict['sense_no'] = sense_no

        soup = OpenDictFetcher.get_soup_by_url(OpenDictFetcher.dictionary_url + sense_no)

        if not soup:
            # print(f'where sense_no: {sense_no}')
            return OpenDictFetcher.NETWORK_ERR, sense_no

        # 표제어
        try:
            target_word = soup.select_one('span.word_head').text
            if not target_word:
                raise Exception
        except (AttributeError, Exception):
            # print(f'Blank page error where sense_no: {sense_no}')
            return OpenDictFetcher.BLANK_ERR, sense_no

        else:
            if self.request_data['word']:
                output_dict['word'] = target_word.replace('-', '')
            if self.request_data['word_hyphen']:
                output_dict['word_hyphen'] = target_word

        # word_no
        if self.request_data['word_no']:
            try:
                output_dict['word_no'] = re.findall(r"\d+", soup.select_one('a.btn_edit')['href'])[0]
            except (TypeError, AttributeError):
                # 표준국어대사전 등재 X or 관용어구
                output_dict['word_no'] = ''

        # 원어
        if self.request_data['org']:
            org = soup.select_one('button.chi_info.hanja_font').text[1:-5]
            output_dict['org'] = org if org else output_dict['word']

        # 원어 분석
        if self.request_data['org_part']:
            org_tbl = soup.select_one('table#orglang_tbl')

            org_part = []
            try:
                for td, th in zip(org_tbl.select('td'), org_tbl.select('th')):
                    if td.select_one('div')['class'][0] == 'hanja':
                        org_part.append((th.text, ''.join([x.text for x in td.select('dt.hanja_font')])))
                    else:  # 'text'
                        org_part.append((th.text, td.text))
            except AttributeError:
                pass
            output_dict['org_part'] = org_part

        # word_head box 부분 데이터
        for elem in soup.select('div.word_head_txt > dl'):
            head_info_type = elem.select_one('dt').text

            # 발음 + 발음 파일
            if head_info_type == '발음':

                # 발음
                if self.request_data['sound']:
                    output_dict['sound'] = elem.select_one('span').text[1:-1].split('/')

                # 발음 파일 주소
                if self.request_data['sound_url']:
                    try:
                        sound_file_no_list = [x['data-file-no'] for x in elem.select('span.search_sub > img')]
                    except TypeError:
                        pass
                    else:
                        output_dict['sound_url'] = []
                        for sound_file_no in sound_file_no_list:
                            media_request_data = {'file_no': sound_file_no, 'file_kind': 'S'}
                            media_rq = requests.post('https://opendict.korean.go.kr/files/link',
                                                     data=media_request_data,
                                                     verify=False)
                            media_rq_output = json.loads(media_rq.text)['json']
                            sound_file_url = media_rq_output[1] if media_rq_output[0] == 'SUCCESS' else ''
                            output_dict['sound_url'].append(sound_file_url)

            # 활용 형태
            elif head_info_type == '활용' and self.request_data['conj_form']:
                output_dict['conj_form'] = elem.select_one('span.search_sub').text

            # 분류
            elif head_info_type == '분류' and self.request_data['class']:
                output_dict['class'] = re.compile('[^ㄱ-ㅣ가-힣]+').sub('', elem.select_one('span').text)

            # 분야
            elif head_info_type == '분야' and self.request_data['field']:
                output_dict['field'] = re.sub("[『』]", '', elem.select_one('span.word_att_type2').text)

            # 분류/분야
            elif head_info_type == '분류/분야':
                raw_class_field = elem.select('span')
                if self.request_data['class'] and self.request_data['class']:
                    output_dict['class'] = raw_class_field[0].text[1:-1]
                if self.request_data['field'] and self.request_data['field']:
                    output_dict['field'] = raw_class_field[1].text[1:-1]

            # 품사
            elif head_info_type == '품사' and self.request_data['pos']:
                output_dict['pos'] = re.compile('[^ㄱ-ㅣ가-힣]+').sub('', elem.select_one('span').text)

            # 품사/문형 - 용언?
            elif head_info_type == '품사/문형':
                raw_pos_pattern = elem.select_one('span').text.split('」')
                if self.request_data['pos']:
                    output_dict['pos'] = raw_pos_pattern[0][1:]
                if self.request_data['pattern']:
                    output_dict['pattern'] = raw_pos_pattern[1][1:]

            # 학명~
            elif re.search(r'[학과목강문]명', head_info_type) and self.request_data['sci_name']:
                output_dict['sci_name'] = elem.select_one('span').text

            # 예외 처리
            else:
                print(f"NOT DEFINED INFO TYPE: {head_info_type} where sense_no: {sense_no}")

        # 단어 번호
        if self.request_data['hg_word_no']:
            output_dict['hg_word_no'] = soup.select_one('span.word_no').text[1:-1]

        # 뜻풀이
        if self.request_data['def']:
            output_dict['def'] = soup.select_one('span.word_dis').text

        # 예문
        if self.request_data['ex']:
            output_dict['ex'] = []

            for dd in soup.select('dl.cont_01.mt20 > dd'):
                example_split = dd.text.replace('\n', '').strip().split('≪')
                if len(example_split) == 2:
                    output_dict['ex'].append((example_split[0], example_split[1][:-1]))
                else:
                    output_dict['ex'].append((example_split[0], ''))

        # 수화(한국 수어 사전 번호)
        if self.request_data['hand_no']:
            try:
                output_dict['hand_no'] = re.findall(r"\d+", soup.select_one('a.floatR.btn_sm.btn_blank')['onclick'])[0]
            except TypeError:
                pass

        # 연관 단어
        if self.request_data['related']:
            try:
                json_str = re.sub(r',\"group\":\"(\w|\s)*\"', '', soup.select_one('div#wordmap_json_str').text)
            except AttributeError:
                pass
            else:
                # TODO: ......^^;;
                jd = json.loads(json_str)['children']
                output_dict['related'] = {}
                for m in jd:
                    output_dict['related'][m['name']] = []
                    for mc in m['children']:
                        if mc['name'] == '전체' and 'sense_no' not in mc:
                            for tc in mc['children']:
                                output_dict['related'][m['name']].extend(tc['children'])
                        else:
                            output_dict['related'][m['name']].append(mc)

        # Check null values in output_data
        for rq in self.request_data.keys():
            if rq not in output_dict:
                output_dict[rq] = ''

        return OpenDictFetcher.SUCCESS, output_dict

    def sense_downloader(self, sense_no_list, thread=None, output_file=None, err_file=None):
        """
        멀티쓰레딩 이용해 주어진 sense_no 들에 해당하는 사전 데이터를 파일 또는 리스트 형태로 반환
        :param sense_no_list: 가져올 단어의 sense_no가 담긴 리스트
        :param thread: 멀티쓰레딩시 사용할 최대 쓰레드 개수. Default=Cpu_count()
        :param output_file: 출력할 파일 주소. 주어지지 않으면 list of dictionaries 반환
        :param err_file: 네트워크 에러 단어 목록 파일 주어지지 않으면 파일 출력 없음
        :return:
        """
        if thread is None:
            thread = multiprocessing.cpu_count()

        output = []
        total_len = len(sense_no_list)
        print("Start downloading...")
        with ThreadPoolExecutor(max_workers=thread) as executor:
            futures = []

            for sn in sense_no_list:
                futures.append(executor.submit(self.get_data_by_sense_no, sn))

            for f in tqdm(as_completed(futures), total=total_len):
                output.append(f.result())

        # process evaluation
        dict_output = [elem[1] for elem in output if elem[0] == OpenDictFetcher.SUCCESS]
        blank_err_output = [elem[1] for elem in output if elem[0] == OpenDictFetcher.BLANK_ERR]
        network_err_output = [elem[1] for elem in output if elem[0] == OpenDictFetcher.NETWORK_ERR]

        print(f"END! {len(dict_output)}/{total_len} -> {(len(dict_output) / total_len) * 100}%")

        if err_file:
            with open(err_file, 'a+') as ef:
                for line in blank_err_output:
                    ef.write(f"B {line}\n")
                for line in network_err_output:
                    ef.write(f"N {line}\n")

        if output_file is None:
            return dict_output
        else:
            with open(output_file, 'w') as f:
                json.dump(dict_output, f, ensure_ascii=False)

