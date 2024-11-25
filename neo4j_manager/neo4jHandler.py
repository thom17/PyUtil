from py2neo import Graph, Node, Relationship
from dataclasses import asdict, dataclass

from typing import Dict, List, Optional, Any, Union

# from neo4j import GraphDatabase
'''
2024-11-18
neomodel vs py2neo
neomodel이 ORM에 더 특화되어 있으나
호환문제로 py2neo를 사용하기로

아래는 모든 타입에 대하여 사용 가능하도록 고려해본 handeler

'''

class Neo4jHandler:
    def __init__(self, uri, user, password, database="neo4j"):
        # self.driver = driver = GraphDatabase.driver(uri, auth=(user, password))
        # self.__create_database(database)
        self.graph = Graph(uri, auth=(user, password), name=database)


    def close(self):
        self.graph = None

    #to do : 여기서 좀 이쁘게 다듬자
    def save_data(self, data: Union[dataclass, List[dataclass]], pid_key: Optional[str] = None):
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

    def __save_data_batch(self, data_list: List[dataclass], pid_key: Optional[str]):
          # 데이터 타입 이름 추출
          # 트랜잭션 명시적으로 관리
          tx = self.graph.begin()  # Transaction 시작
          try:
              for data in data_list:
                  type_name = str(type(data).__name__)
                  if hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
                      data_dict = data.to_dict()
                  else:
                      data_dict = asdict(data)
                  data_node = Node(type_name, **data_dict)
                  if pid_key:
                      data_node.__primarykey__ = pid_key
                      tx.merge(data_node, type_name, pid_key)
                  else:
                      tx.create(data_node)
              tx.commit()  # 트랜잭션 커밋
          except Exception as e:
              tx.rollback()  # 예외 발생 시 롤백
              raise e


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
        for r in self.do_query(query):
            print(f'{r["label"]}\t\t:\t{r["count"]} size')



    def find_node_by_key_value(self, key, value):
        nodes = self.graph.nodes.match("data", **{key: value})
        return [dict(node) for node in nodes]

    def delete_all_nodes(self):
        self.graph.delete_all()

    def add_relationship(self, src_data_name, dst_data_name, rel_type, **properties):
        # 두 노드 찾기
        src_node = self.graph.nodes.match("data", src_name=src_data_name).first()
        dst_node = self.graph.nodes.match("data", src_name=dst_data_name).first()



        if not src_node or not dst_node:
            raise ValueError(f"Source or destination node not found {src_node} / {dst_node}")

        # 관계 생성
        relationship = Relationship(src_node, rel_type, dst_node, **properties)
        self.graph.create(relationship)



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


