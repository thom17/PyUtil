import pytest
from neo4j_manager.neo4jHandler import Neo4jHandler
from dataclasses import dataclass
import time
def test_print_info():
    print(test_print_info)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", database='neo4j', password="123456789")
    handler.print_info()

    # result = handler.do_query("CREATE (n:Person {name: 'Alice', age: 30})")
    # print(result)
    # handler.print_info()

def test_table():
    print(test_table)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", database='newDB', password="123456789")
    print('connect')
    handler.graph.pull()
    handler.graph.commit()
    handler.do_query('CREATE DATABASE newDB')
    handler.print_info()
    handler.do_query("CREATE (n:Class {name: 'Manger', package: 'main'})")
    handler.print_info()

def test_reset():
    print(test_reset)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    handler.delete_all_nodes()
    handler.print_info()


def test_search():
    print(test_update)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    handler.delete_all_nodes()

    @dataclass
    class A:
        x: int
        y: int
        pass

    handler.delete_all_nodes()

    datas = [A( i, i ) for i in range(10)]
    handler.save_data(datas)

    @dataclass
    class A:
        x: int
        y: int
        z: int
        pass

    datas2 = [A( i, i , i**2) for i in range(10)]
    handler.save_data(datas2)

    @dataclass
    class AB:
        x: int
        y: int
        pass

    datas2 = [AB(i, i) for i in range(10)]
    handler.save_data(datas2)




    handler.print_info()
    node_map = handler.search_node_map(datas)

    for data, search_list in node_map:
        print(data)
        print(search_list)
        print()

    datas3 = [(data, f'id_{id(data)}') for data in datas2]
    handler.save_data(datas3)

    node_map = handler.search_node_map(datas3)

    for data, search_list in node_map:
        print(data)
        print(search_list)
        print()

    result = node_map[0][1]
    print((type(result)))
    print(len(result))

def test_relation():
    print(test_relation)
    @dataclass
    class A:
        x: int
        y: int
        pass

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    print('delete before')
    handler.print_info()

    datas = [A(i, i) for i in range(10)]
    handler.delete_all_nodes()
    handler.save_data(datas)
    print('\nafter delete')
    handler.print_info()

    r_list = []
    for i in range(10):
        r_list.append((datas[i], datas[9 - i], f'connect {i%3}'))

    handler.add_relationship(data_list=r_list)
    print('\nadd relation')
    handler.print_info()

def test_update():
    print(test_update)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    handler.delete_all_nodes()
    @dataclass
    class A:
        x: int
        y: int
        pass

    st = time.time()
    for i in range(10):
        a = A(i, i)
        handler.save_data(a)
    ed = time.time()

    handler.print_info()
    print(ed-st, " 데이터 10개 개별 create")

    st = time.time()
    for i in range(10):
        a = A(i, i)
        handler.save_data(a)
    ed = time.time()

    handler.print_info()
    print(ed-st, " 데이터 10개 개별 create (중복 수행)")

    print('key가 중복되므로 삭제 처리')
    handler.delete_all_nodes()

    st = time.time()
    for i in range(10):
        a = A(i, i)
        handler.save_data(a, 'x')
    ed = time.time()

    handler.print_info()
    print(ed-st, " 데이터 10개 개별 merge")

    st = time.time()
    data_li = []
    for i in range(10):
        data_li.append(A(i, i))
        handler.save_data(data_li, 'x')
    ed = time.time()

    handler.print_info()
    print(ed-st, " 데이터 10개 트랜잭션 merge")

    # st = time.time()
    # data_li = []
    # for i in range(100):
    #     data_li.append(A(i, i*i))
    # handler.save_data(data_li, 'x')
    # ed = time.time()
    #
    #
    # handler.print_info()
    # print(ed - st, " 2st times ")
    #
    # st = time.time()
    # data_li = []
    # for i in range(500):
    #     data_li.append(A(400+i, i*i*-1))
    #
    # handler.save_data(data_li, 'x')
    # handler.print_info()
    # ed = time.time()
    #
    # print(ed - st, " 3st times ")

def test_all():
    handler = Neo4jHandler(uri="bolt://localhost:7687", user = "neo4j", password= "123456789")


    result1 = handler.do_query("MATCH (n) RETURN n.name AS name, n.age AS age")
    result2 = handler.do_query("MATCH (n) RETURN count(n) AS total_nodes")
    result2_2 = handler.do_query("MATCH (n) RETURN count(n) as size")

    result3 = handler.get_node_count()
    print('size ', result3)
    print(result1)
    print(result2)
    print(result2_2)


    result3 = handler.do_query("CREATE (n:Person {name: 'Alice', age: 30})")
    print(result3)


    print('-'*10)
    handler.print_info()

    @dataclass
    class A:
        x: int

        pass


    class AB(A):
        pass

    a=A(0)
    ab=AB(1)

    print(str(type(a).__name__))
    print(str(type(ab).__name__))
    print(str(type(handler).__name__))
    print()

    print(type(ab).__str__)
    print(type(ab).__bases__)


    handler.save_data(a)
    handler.save_data(ab)

def test_use_data2node():
    print(test_use_data2node)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    handler.delete_all_nodes()

    @dataclass
    class A:
        x: int
        y: int

    st = time.time()
    datas = [A(i, i) for i in range(10)]
    handler.save_data(datas)
    ed = time.time()
    handler.print_info()
    print(ed-st, "Add A")

    st = time.time()
    nodes = [(handler.data2node(data), f'A_{data.x}') for data in datas]
    handler.save_data(nodes)
    ed = time.time()
    handler.print_info()
    print(ed - st, "Add A_ID")

def test_update_relation():
    '''
    Merge 후 Relation 유지 여부 확인
    :return:
    '''
    print(test_update_relation)

    handler = Neo4jHandler(uri="bolt://localhost:7687", user="neo4j", password="123456789")
    handler.delete_all_nodes()

    @dataclass
    class A:
        x: int
        y: int

    st = time.time()
    datas = [A(i, i) for i in range(10)]
    handler.save_data(datas)
    ed = time.time()
    handler.print_info()
    print(ed-st, "Add A")

    st = time.time()
    ref = [(datas[i], datas[i+1], 'next') for i in range(9)]
    handler.add_relationship(data_list=ref)
    ed = time.time()
    handler.print_info()
    print(ed-st, "Add ref")

    st = time.time()
    datas = [A(i, i * -1) for i in range(10)]
    handler.save_data(datas, pid_key='x')
    ed = time.time()
    handler.print_info()
    print(ed-st, "Update A")
