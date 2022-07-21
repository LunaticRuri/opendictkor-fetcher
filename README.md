# opendictkor-fetcher

국립국어원에서 제공하는 오픈 사전 우리말샘(https://opendict.korean.go.kr/) 크롤러

2022/7/21 기준이라 이후에는 정상 작동하지 않을 수 있음

공식 OpenAPI(https://opendict.korean.go.kr/service/openApiInfo) 제공됨 - OpenAPI 사용하기 곤란할 때?

## 설치

```shell
$ python setup.py install
```

또는

dist 폴더의 wheel 파일 받아 

```shell
$ pip install opendictkor_fetcher-1.0-py3-none-any.whl
```

## 데이터 설명
- 'sense_no': 우리말샘에서 사용되는 구분 id
- 'word': 단어
- 'word_hyphen': 하이픈으로 구분된 단어
- 'word_no': 표준국어대사전에서 사용되는 구분 id
- 'org': 원어
- 'org_part': 부분별로 분석된 원어
- 'sound': 발음
- 'sound_url': 발음 파일 주소
- 'conj_form': 활용
- 'class': 분류
- 'field': 분야
- 'pos': 품사
- 'pattern': 문형
- 'sci_name': 학명
- 'hg_word_no': 동형이의어 의미 번호 (001~)
- 'def': 뜻풀이
- 'ex': 예문
- 'hand_no': 한국 수어 사전에서 사용되는 구분 id
- 'related': 연관어(상위어, 본말/준말, 비슷한말, 참고 어휘, 하위어, 낮춤말, 반대말, 높임말)

## 사용

