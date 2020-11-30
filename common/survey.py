from random import randint

SURVEY_ID = 6
SURVEY_URL = "/survey/show/test2/"
DRAFT_URL = SURVEY_URL + "?draft=save"


def get_draft():
    return {
        "survey_id": SURVEY_ID,
        "form_data": {
            "PREFIL_BIRTHYEAR": "1950",
            "TestRegEx": "",
            "testChild": "NULL",
            "OpenDate": "",
            "OpenNumeric": str(randint(1, 999)),
            "TestMatrixEntries_multi_row1_col1": "",
            "TestMatrixEntries_multi_row1_col2": "",
            "TestMatrixEntries_multi_row2_col1": "",
            "TestMatrixEntries_multi_row2_col2": "",
            "TestMatrixEntries_multi_row3_col1": "",
            "TestMatrixEntries_multi_row3_col2": ""
        }}


def get_data(token: str):
    return {
        'csrfmiddlewaretoken': token,
        'PREFIL_BIRTHYEAR': '1950',
        'TestRegEx': 'A',
        'TestSC': 'S',
        'TestSC_S_open': '34',
        'testChild': 'NULL',
        'TestAdult': 'Y',
        'OpenDate': str(randint(1, 28)) + '/08/2017',
        'OpenNumeric': str(randint(1, 790)),
        'TestMC_B': '1',
        'TestMC_M': '1',
        'TestSufficient': 'Y',
        'TestSuff2': 'Y',
        'UncheckTest': 'REMOPT',
        'TestQ': 'T',
        'TestFill': 'FILL',
        'TestMatrixEntries_multi_row1_col1': '',
        'TestMatrixEntries_multi_row1_col2': '',
        'TestMatrixEntries_multi_row2_col1': 'Banana!',
        'TestMatrixEntries_multi_row2_col2': '',
        'TestMatrixEntries_multi_row3_col1': '',
        'TestMatrixEntries_multi_row3_col2': ''
    }
