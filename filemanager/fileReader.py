import chardet

def read_file(file_path: str) -> str:
    '''
    파일을 읽어 문자열로 반환 (인코딩 인식 및 처리 포함)
    '''
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        file_encode = chardet.detect(raw_data)['encoding']

        # 파일 읽기
        with open(file_path, 'r', encoding=file_encode) as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def get_encode(file_path: str) -> str:
    '''
    파일의 인코딩을 감지하여 반환
    '''
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        return chardet.detect(raw_data)['encoding']
    except Exception as e:
        print(f"Error detecting encoding for file {file_path}: {e}")
        return ""

def write_file(file_path: str, context : str, encode = None) -> str:
    '''
    파일을 읽어 문자열로 반환 (인코딩 인식 및 처리 포함)
    '''
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        file_encode = chardet.detect(raw_data)['encoding']

        with open(file_path, 'r', encoding=file_encode) as file:
            before_text = file.read()

        if encode is None:
            encode = file_encode

        with open(file_path, 'w', encoding=encode) as file:
            file.write(context)
        return before_text
    except Exception as e:
        print(f"Error write file {file_path}: {e}")
        return ""