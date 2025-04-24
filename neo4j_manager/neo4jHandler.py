from py2neo import Graph, Node, Relationship
from dataclasses import asdict, dataclass, is_dataclass

from typing import Dict, List, Optional, Any, Union, Tuple, overload

from collections.abc import Iterable

from neo4j import GraphDatabase
'''
2024-11-18
neomodel vs py2neo
neomodel이 ORM에 더 특화되어 있으나
호환문제로 py2neo를 사용하기로

아래는 모든 타입에 대하여 사용 가능하도록 고려해본 handeler

'''
DataInput = Union[
    dataclass, #단일 dataclass
    List[dataclass], #다중 dataclass
    Tuple[dataclass, str], #단일 dataclass와 label
    List[Tuple[dataclass, str]] #다중 dataclass와 label
]

class Neo4jHandler:
    def __init__(self, uri, user, password, database="neo4j"):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__database = database

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        if not database in self.show_databases(): #databse 여부 확인
            self.create_database(database)

        self.graph = Graph(uri, auth=(user, password), name=database)

    def show_databases(self) -> List[str]:
        names = []
        with self.driver.session(database="system") as session:
            result = session.run("SHOW DATABASES")
            for record in result:
                names.append(record['name'])
        return names

    def create_database(self, database_name: str):
        driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__password))

        def create_database(tx, database_name):
            tx.run(f"CREATE DATABASE {database_name}")

        with driver.session(database="system") as session:
            session.write_transaction(create_database, database_name)

    def close(self):
        self.graph = None

    data: Union[dataclass, List[dataclass], Tuple[dataclass, str], List[Tuple[dataclass, str]]]

    #to do : 여기서 좀 이쁘게 다듬자
    def save_data(self, data: DataInput, pid_key: Optional[str] = None):
        '''
        add or update 
        Args:
            data: 추가할 데이터, 복수라면 리스트
            pid_key: 식별 키 가 없을 경우 모든 데이터가 중복이 아니라면 추가 
        '''
        if isinstance(data, List):
            return self.__save_data_batch(data_list=data, pid_key=pid_key)
        else:
            return self.__save_data_batch(data_list=[data], pid_key=pid_key)



        # data_dict = asdict(data)
        # type_name= str(type(data).__name__)
        # data_node = Node(type_name, **data_dict)
        # if pid_key:
        #     data_node.__primarykey__ = pid_key
        #     self.graph.merge(data_node, type_name, pid_key)
        # else:
        #     self.graph.create(data_node)

        # self.graph.merge(data_node, type_name, "src_name")

    def __data2dict(self, data: Any, check_str: bool = False) -> Dict[str, Any]:
        """
        Converts the provided data to a dictionary.

        Args:
            data (Any): The input data to be converted. It can be a dataclass,
                        an object with a 'to_dict' method, or a dictionary.
            check_str (bool): If True, converts all non-string values in the
                              resulting dictionary to strings.

        Returns:
            Dict[str, Any]: A dictionary representation of the input data.

        Raises:
            TypeError: If the provided data is not a dictionary, does not have
                       a 'to_dict' method, and is not a dataclass.
        """
        # If data is already a dictionary, use it as is
        if isinstance(data, dict):
            data_dict = data
        # Check if the object has a 'to_dict' method
        elif hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
            data_dict = data.to_dict()
        # Check if the data is a dataclass
        elif is_dataclass(data):
            data_dict = asdict(data)
        else:
            # Raise an error if the data cannot be converted to a dictionary
            raise TypeError(f"dict을 변환 불가. {type(data)}")

        # Convert non-string values to strings if check_str is True
        if check_str:
            for key, value in data_dict.items():
                if not isinstance(value, str):
                    data_dict[key] = str(value)

        return data_dict

    def __get_node_name(self, data: Any) -> str:
        return str(type(data).__name__)

    def data2node(self, data: Any, check_str: bool = False) -> Node:
        '''

        Args:
            data:
            check_str:

        Returns:

        '''
        type_name = self.__get_node_name(data)
        data_dict = self.__data2dict(data, check_str)
        data_node = Node(type_name, **data_dict)

        return data_node

    def __save_data_batch(self, data_list: List[Union[dataclass, Tuple[dataclass, str]]], pid_key: Optional[str]):
          '''
          add or update 
            Args:
                data_list: 추가할 데이터 
                pid_key: 식별 키 가 없을 경우 모든 데이터가 중복이 아니라면 추가 
          '''
          # 데이터 타입 이름 추출
          # 트랜잭션 명시적으로 관리
          tx = self.graph.begin()  # Transaction 시작
          try:
              for data in data_list:
                  if isinstance(data, Tuple):
                      type_name = data[1]
                      data = data[0]
                  else:
                    type_name = str(type(data).__name__)


                  data_dict = self.__data2dict(data)
                  data_node = Node(type_name, **data_dict)

                  #특정 키만 같다면 업데이트
                  if pid_key: 
                      data_node.__primarykey__ = pid_key
                      tx.merge(data_node, type_name, pid_key)
                  else: #모든 속성 중 하나라도 다르면 추가
                      tx.merge(data_node, type_name, tuple(data_dict.keys())) 
              tx.commit()  # 트랜잭션 커밋
          except Exception as e:
              tx.rollback()  # 예외 발생 시 롤백
              raise e


    def add_relationship(self, data_list: List[ Tuple [dataclass, dataclass, str] ], **properties):
        ''' 2024-12-05:
        입력을 다듬을 필요가 있어보이는대..
        Args:
            Tuiple (data, data, rel_nam:str)
            **properties:

        Returns:
        '''
        def convert_node_list(data_list: List[ Tuple [dataclass, dataclass]], self = self) -> List[Tuple[Node, Node]]:
            convert_nodes = []
            for idx, (data1, data2, rel_type) in enumerate(data_list):
                search_map = self.search_node_map([data1, data2])
                node1_list =search_map[0][1]
                assert len(node1_list) == 1, f'식별 불가능({len(node1_list)})개 검색됨.\ndata_list[{idx}[0]] {data1}'

                node2_list =search_map[1][1]
                assert len(node2_list) == 1, f'식별 불가능({len(node2_list)})개 검색됨.\ndata_list[{idx}[1]] {data2}'

                convert_nodes.append((node1_list[0], node2_list[0], rel_type))
            return convert_nodes


        if not isinstance(data_list, List):
            data_list = [data_list]

        node_list = convert_node_list(data_list=data_list)

        tx = self.graph.begin()
        try:
            for node1, node2, rel_type in node_list:
                relationship = Relationship(node1, rel_type, node2, **properties)
                tx.create(relationship)
            tx.commit()
        except Exception as e:
            tx.rollback()  # 예외 발생 시 롤백
            raise e


        # type_name = str(type(data).__name__)


    def search_node_map(self, datas: DataInput) -> List[Tuple[Any, List[Node]]]:
        '''
        원래는 map(dict)이어야 하지만 data들이 hash 되지 않을 수 있음
        Args:
            datas: 검색할 객체들

        Returns: List [객체, List[검색결과]]

        '''
        result_list: List[Tuple[Any, List[Node]]] = []
        if isinstance(datas, Iterable) and not isinstance(datas, (str, bytes, dict)):
            for data in datas:
                result_list.append((data, self.__match_nodes(data)))
        else:
            result_list.append((datas, self.__match_nodes(datas)))
        return result_list


    def __match_nodes(self, data: Union[dataclass, Tuple[dataclass, str]]) -> List[Node]:
        if isinstance(data, Tuple):
            node_name = data[1]
            data = data[0]
        else:
            node_name = self.__get_node_name(data)

        data_dict: Dict = self.__data2dict(data)
        return list(self.graph.nodes.match(node_name, **data_dict))


    # def add_relationship(self, data_list: List[ Tuple[ Tuple[dataclass, str],  Tuple[dataclass, str]] ], rel_type: str, **properties):



    def do_query(self, query: str)-> List[Dict[str, Any]]:
        return self.graph.run(query).data()

    def get_all_node_size(self):
        return self.do_query("MATCH (n) RETURN count(n) as size")[0]['size']

    def print_info(self):

        query = """
        MATCH (n)
        WITH labels(n) AS labels
        UNWIND labels AS label
        RETURN label, count(*) AS count
        """

        print('Nodes')
        for r in self.do_query(query):
            print(f'\t{r["label"]}\t\t:\t{r["count"]} size')

        # 관계 정보 출력
        query_rels = """
        MATCH ()-[r]->()
        RETURN type(r) AS rel_type, count(*) AS count
        """

        print('Relationships')
        for r in self.do_query(query_rels):
            print(f'\t{r["rel_type"]}\t\t:\t{r["count"]} size')

    def find_node_by_key_value(self, key, value):
        nodes = self.graph.nodes.match("data", **{key: value})
        return [dict(node) for node in nodes]

    def delete_all_nodes(self):
        self.graph.delete_all()



if __name__ == "__main__":
    import time
    start_time = time.time()
    neo4j_handler = Neo4jHandler("bolt://localhost:7687", "neo4j_manager", "123456789")


    @dataclass
    class A:
        a: str
        b: str
    a = A('a', 'b')

    @dataclass
    class B:
        a: str
        b: str
    b = B('x', 'y')

    neo4j_handler.save_data(a, 'a')
    neo4j_handler.save_data(b, 'a')
    neo4j_handler.close()

    # all_info_objects = neo4j_handler.read_all_nodes()
    # src_map = all_info_objects.get_src_map()


