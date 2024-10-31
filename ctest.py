import clang.cindex
from clang.cindex import Cursor as clangCursor
from clang.cindex import SourceLocation
from clang.cindex import TranslationUnit
from clang.cindex import SourceRange
from clang.cindex import CursorKind

from collections import defaultdict
from typing import Dict, List

# to do: 이거 왜 에러나지?
if __name__ == "__main__":
    import clang_utill as ClangUtil
else:
    import clangParser.clang_utill as ClangUtil

import chardet  # for py 11
# import cchardet as chardet
import os

from sympy.physics.units import force


class Cursor:
    """
    clang.cindex.Cursor 가 불편해서 정의
    """

    def __init__(self, node: clangCursor, source_code: str = None):
        assert isinstance(node, clangCursor), f"node{type(node)} must be an instance of clang.cindex.Cursor"
        self.node = node
        self.is_def = node.is_definition()
        self.spelling = node.spelling
        self.location: SourceLocation = node.location
        self.extend: SourceRange = node.extent
        self.kind: str = node.kind.name
        self.translation_unit: TranslationUnit = node.translation_unit
        self.unit_path: str = self.translation_unit.spelling
        self.source_code = source_code
        self.line_size = None

        self.line_size = self.get_line_size()

        # try:
        #     if self.unit_path:
        #         with open(self.unit_path, 'r') as file:
        #             self.unit_source_code = file.read()
        #
        #         if self.location.file:
        #             with open(self.location.file.name, 'r') as file:
        #                 self.node_source_code = file.read()
        #         else:
        #             self.node_source_code = self.unit_source_code
        # except:
        #     print("error ",node.location)

    def get_range(self):
        start: SourceLocation = self.extend.start
        end: SourceLocation = self.extend.end

        return f"{start.line}:{start.column}~{end.line}:{end.column}"

    def get_line_size(self) -> int:
        # 해당 커서가 몇 줄인지 반환

        if self.line_size is None:
            start: SourceLocation = self.extend.start
            end: SourceLocation = self.extend.end
            self.line_size = end.line - start.line + 1
        return self.line_size

    def to_dict(self):
        # Convert to a dictionary or other JSON-serializable format
        location = {
            'file': self.location.file.name if self.location.file else None,
            'line': self.location.line,
            'column': self.location.column
        }

        start: SourceLocation = self.extend.start
        end: SourceLocation = self.extend.end

        range = {
            'startLine': start.line,
            'startColumn': start.column,
            'endLine': end.line,
            'endColumn': end.column,
        }
        return {
            'spelling': self.spelling,
            'kind': self.kind,
            'range': range,
            'location': location,
            'code': self.get_range_code()
        }

    def get_visit_def_map(self, node=None) -> [str, clangCursor]:
        visit_map: [str, 'clangCursor'] = {}  # 1:1 대응으로 바꿔도 문제없어야 함
        if node is None:
            node = self.node
        queue = [node]
        while queue:
            node = queue.pop(0)
            if node.is_definition():
                visit_map[Cursor(node).get_src_name()] = node
            queue.extend(node.get_children())
        return visit_map

    def get_in_tab(self) -> str:
        line_code = self.get_range_line_code()
        start = self.location.column
        intab = line_code[:start - 1]

        # print(line_code)
        # print(intab, 'Intab')
        assert intab, f'err in tab'
        return intab

    def search_context_node(self, context) -> Dict[int, List['Cursor']]:
        '''
        clnag에서 정상적으로 파싱이 안되는 경우가 있다.
        따라서 <LineNum, []> 형태로 반환하여 줄번호로도 추적되게
        :param context: 찾고자하는 키워드
        :return:
        '''

        result_search = {}

        range_code_lines = self.get_range_code().splitlines()
        target_line_list = []
        for idx, line in enumerate(range_code_lines):
            if context in line:
                target_line_list.append(self.location.line + idx)

        line_map = self.get_visit_line_map()

        for line in target_line_list:
            node_list = []
            if line in line_map:
                for node in line_map[line]:
                    if node.get_line_size() == 1 and context in node.get_range_code():
                        node_list.append(node)

            result_search[line] = node_list
        return result_search

    def get_src_name(self, node=None):
        """
        그 srcName
        클래스.메서드.메서드.변수, 파일.변수, 파일.매서드
        정리되기 전까지는 특정 노드만 사용하자
        :return:
        """

        if node is None:
            node = self.node

        assert node, "Node is null"

        return ClangUtil.get_src_name(node)

    def get_call_definition(self, target_stmt=None):
        """
        DFS로 target_stmt의 defintion node를 구한다.
        :param target_stmt:
        :return:
        """
        dec_list: ['Cursor'] = []
        dec_list: ['Cursor'] = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            kind = node.kind
            if target_stmt is None:
                target_stmt = node.kind.get_all_kinds()

            if kind in target_stmt:
                def_node = node.get_definition()
                if def_node:
                    new_cursor = get_cursor(def_node)
                    dec_list.append(new_cursor)
            queue[:0] = node.get_children()
        return dec_list

    def get_call_definition_map(self) -> Dict[clangCursor, clangCursor]:
        """
        DFS로 target_stmt의 defintion node를 구한다.
        :param target_stmt:
        :return dec_dict: [call_node: clangCursor, def_node: clangCursor]
        """
        dec_dict: [clangCursor, clangCursor] = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            def_node = node.get_definition()
            if def_node:
                dec_dict[node] = def_node
            queue[:0] = node.get_children()
        return dec_dict

    def read_file(self) -> (str, int):
        """
        해당 노드의 파일 읽기. 우선순위도 함께 반환
        1. range 코드
        2. location Code
        3. unit path
        :return:
        """

        extent = self.node.extent
        start = extent.start
        end = extent.end

        mod = None
        while True:
            if start.file and end.file and start.file.name == end.file.name and not mod:
                mod = 1
                file_path = start.file.name
            elif self.location.file and mod != 2:
                mod = 2
                file_path = self.location.file.name
            elif mod != 3:
                mod = 3
                file_path = self.translation_unit.spelling
            else:
                assert True, "Read File Fail"
                return "", mod
            try:
                # 먼저 파일 인코딩 방식 탐지
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                file_encode = chardet.detect(raw_data)['encoding']

                # 파일 읽기
                with open(file_path, 'r', encoding=file_encode) as file:
                    return file.read(), mod

            except:
                print(f"{file_path}  read Fail")
                return "", mod

    def get_range_code(self) -> str:
        """
        Returns the source code for the specific range including column information.
        """

        source_code, mod = self.read_file()

        if mod == 1:
            extent = self.node.extent
            start = extent.start
            end = extent.end

            start_index = self.calculate_offset(source_code, start.line, start.column)
            end_index = self.calculate_offset(source_code, end.line, end.column)

            return source_code[start_index:end_index]
        else:
            line = source_code.splitlines()[self.location.line - 1]
            return line[self.location.column - 1:]

    def get_range_line_code(self):
        """
        Returns the entire lines of code from the start to the end line without considering the columns.
        """
        extent = self.node.extent
        start = extent.start
        end = extent.end

        assert start.file.name == end.file.name, "Start and end are in different files."

        # 먼저 파일 인코딩 방식 탐지
        with open(start.file.name, 'rb') as file:
            raw_data = file.read()
        file_encode = chardet.detect(raw_data)['encoding']

        # 파일 읽기
        with open(start.file.name, 'r', encoding=file_encode) as file:
            lines = file.readlines()

            # Lines are 0-based in Python, adjust by -1 since Clang lines are 1-based
            return ''.join(lines[start.line - 1:end.line])

    def calculate_offset(self, source_code, line, column):
        """
        Calculates the offset of the specified line and column in the source code.
        """
        current_line = 1
        offset = 0
        # Iterate through the source code line by line
        for current_line_content in source_code.split('\n'):
            if current_line == line:
                # Columns are 1-based, adjust by -1 for 0-based indexing
                return offset + (column - 1)
            offset += len(current_line_content) + 1  # +1 for newline character
            current_line += 1

        return offset  # If line/column are out of bounds, this will be the end of the source code

    def get_visit_line_token_map(self, node=None) -> dict[int, [clang.cindex.Token]]:
        line_map = {}
        if node is None:
            node = self.node
        for token in node.get_tokens():
            line: int = token.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(token)
        return line_map

    def get_visit_kind_token_map(self, node=None) -> dict[str, [clang.cindex.Token]]:
        kind_map = {}
        if node is None:
            node = self.node
        for token in node.get_tokens():
            kind = token.kind
            if kind not in kind_map:
                kind_map[kind] = []
            kind_map[kind].append(token)
        return kind_map

    def get_visit_line_map(self) -> Dict[int, List['Cursor']]:
        line_map = {}
        queue = [self.node]
        if self.location.file:
            base_file_path = self.location.file.name
        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            line: int = node.location.line
            if line not in line_map:
                line_map[line] = []
            line_map[line].append(c)
            queue.extend(node.get_children())
        return line_map

    def get_file_map(self) -> {str, list}:
        file_map = {}
        queue: [clangCursor] = [self.node]
        file_name = self.location.file.name if self.location.file else "None"

        while queue:
            node = queue.pop(0)
            new_cursor = get_cursor(node)
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(new_cursor)
            queue.extend(node.get_children())
        return file_map

    def get_visit_type_map(self) -> dict[str, list]:
        stmt_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            type_name: str = node.kind.name
            if type_name not in stmt_map:
                stmt_map[type_name] = []
            stmt_map[type_name].append(c)
            queue.extend(node.get_children())
        return stmt_map

    def get_stmt_list(self) -> ['Cursor']:
        stmt_list = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            if node.kind.is_statement():
                stmt_list.append(get_cursor(node))
            queue.extend(node.get_children())
        return stmt_list

    def get_stmt_map(self) -> Dict['Cursor', List['Cursor']]:
        stmt_map = defaultdict(list)
        self.__visit_stmt(stmt_map=stmt_map, key=self)

        return stmt_map

    def __visit_stmt(self, stmt_map: ['Cursor', ['Cursor']], key: 'Cursor'):
        for node in key.node.get_children():
            c = get_cursor(node)
            stmt_map[key].append(c)

            if node.kind.is_statement():
                self.__visit_stmt(stmt_map=stmt_map, key=c)

    def get_visit_line_size_map(self) -> dict[int, ['Cursor']]:
        line_size_map = defaultdict(list)
        queue = [self.node]

        while queue:
            node: clangCursor = queue.pop(0)
            c: Cursor = get_cursor(node)
            line_size = c.get_line_size()
            line_size_map[line_size].append(c)
            queue.extend(node.get_children())
        return line_size_map

    # '''
    # 각 h의 위치를 어떤식으로 찾을지.... 흠..
    # {
    #     h1
    #     {
    #         h2
    #     }
    #     h3
    #     {
    #     }
    # }
    # '''
    # def find_in_block(self, lines: [int]) -> 'Cursor':
    #     #해당 lines가 속한 최소 크기의 block 을 구한다. (return Cursor)
    #     if isinstance(lines, int):
    #         lines = [lines]
    #
    #     line_size_map = self.get_visit_line_size_map()
    #     for line_size, node_list in sorted(line_size_map.items()):
    #         line_size.
    #
    #     for type_name in self.get_visit_type_map().:
    #
    #     visit_line_map = self.get_visit_line_map()

    def visit_print(self):
        queue = [(self.node, "")]

        while len(queue):
            node, lv = queue.pop(0)
            print(f"{lv}{node.spelling} ({node.kind} {node.location.line}:{node.location.column})")
            c = get_cursor(node)
            print(c.get_range_code())
            # Update the level indicator for child nodes
            new_lv = lv + "* "

            # Prepare child nodes to be added to the queue
            childs = [(child, new_lv) for child in node.get_children()]
            queue = childs + queue

    def visit_nodes(self) -> [clangCursor]:
        visit_list: ['Cursor'] = []
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            visit_list.append(node)
            queue[:0] = node.get_children()
        return visit_list

    def get_visit_unit_map(self) -> dict[TranslationUnit, list['Cursor']]:
        unit_map = {}
        queue = [self.node]

        while queue:
            node = queue.pop(0)
            c = get_cursor(node)
            unit = node.translation_unit
            if unit not in unit_map:
                unit_map[unit] = []
            unit_map[unit].append(c)
            queue.extend(node.get_children())
        return unit_map

    def get_simple_file_name(self, node=None):
        if node is None:
            node = self

        if isinstance(node, Cursor) or isinstance(node, clangCursor):
            path = node.location.file.name

        # 경로를 표준화합니다.
        normalized_path = os.path.normpath(path)

        # 경로를 구성하는 파트들을 리스트로 분리합니다.
        parts = normalized_path.split(os.sep)

        # 마지막 파일 이름과 그 바로 상위 디렉토리만 포함하도록 조정합니다.
        if len(parts) > 1:
            result_path = os.path.join(parts[-2], parts[-1])
        else:
            result_path = parts[-1]  # 파일 또는 폴더만 있는 경우

        return result_path

    def make_comment_code(self, code: str = None):
        """
        재귀적으로 순환해서 노드의 정보를 주석화
        :param code: None은 시작 그외 재귀시 파라미터로
        :return:
        """
        source_name = self.translation_unit.spelling

        if code is None:
            with open(source_name, 'r') as file:
                code = file.read()

        code2list = code.splitlines()

        extent = self.node.extent
        start = extent.start
        end = extent.end

        line = start.line
        # 현재 노드에 대한 주석 추가
        # try:
        #     code2list[line - 1] += f" // {self.node.kind.name}({self.node.spelling})"
        # except:
        #     print(f"line={line} size = {code2list.__len__()}")
        # code = '\n'.join(code2list)
        #
        # # 모든 자식 노드에 대해 재귀적으로 처리
        # for child in self.node.get_children():
        #     child_visitor = SimpleVisitor(child, self.base_path)
        #     code = child_visitor.make_comment_code(code)
        #
        # return code

    def print_node(self, node=None):
        if node:
            print(f"{node.kind}")
            # print(f"{self.get_range_code()}")
            print(f"display : {node.displayname}")
            print(f"spelling : {node.spelling}")
            print(f"{node.location}")
            print(f"{node.extent}")
        else:
            print(f"{self.node.kind}")
            print(f"{self.get_range_code()}")
            print(f"display : {self.node.displayname}")
            print(f"spelling : {self.node.spelling}")
            print(f"{self.node.location}")
            print(f"{self.node.extent}")

    def __str__(self):
        return f"Cursor({self.kind}, {self.spelling}, {self.node.location})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, clangCursor):
            return self.node == other
        elif isinstance(other, Cursor):
            return self.node == other.node

    def __hash__(self):
        return hash(self.node)


cursor_map = {}


def get_cursor(cursor) -> Cursor:
    """
    원래는 ClangCursor : MyCursor로 대응시키려고 만든 메서드였다.
    먼가 버전 이슈로 key로 사용할 수 없고 OMS로 확장하기도 해서 1:1 대응하지 않기로
    :param cursor:
    :return:
    """
    if isinstance(cursor, Cursor):
        assert (cursor_map[cursor.node] == cursor), "cursor map 오류"
        return cursor
    else:
        return Cursor(cursor)
        # assert isinstance(cursor, clangCursor), f"타입 오류 {type(cursor)}"
        # if cursor in cursor_map:
        #     return cursor_map[cursor]
        # else:
        #     cursor_map[cursor] = Cursor(cursor)
        #     return cursor_map[cursor]


if __name__ == "__main__":
    # with open(r"D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\DSILibraryDrawer.cpp", 'r') as file:
    #     print(file.read())
    import clangParser
    import time

    start_time = time.time()
    compliationunit = clangParser.parsing(
        r"D:\dev\AutoPlanning\Pano\changeMerge\mod_APImplantSimulation\ActuatorHybridFixture.cpp")
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Parsing time:", elapsed_time, "seconds")

    mycursor = Cursor(compliationunit.cursor)
    # = get_cursor(compliationunit.cursor)

    start_time = time.time()
    line_map = mycursor.get_visit_line_map()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("Visit time:", elapsed_time, "seconds")

    for line in line_map:
        print(line, end=" ")
        for node in line_map[line]:
            print(f"{node.kind}({node.spelling})")
        print()
    print(mycursor.visit_print())

    same = compliationunit == mycursor.node.translation_unit
    print("is ", same)

    print(mycursor.get_range_code())

    stmt_map = mycursor.get_visit_type_map()

    for type_name in stmt_map:
        cursor_list = stmt_map[type_name]
        print(f"{type_name} : {cursor_list.__len__()} size")

    expr_list = stmt_map["CALL_EXPR"]
    print(type(expr_list))
    for c in expr_list:
        print(c)
        print(f"{c.get_range_code()} @{c.spelling}")

    line_map = mycursor.get_visit_line_map()
    for num in line_map:
        print(num, line_map[num])

    print("done")
