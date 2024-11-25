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

    result3 = handler.get_all_node_size()
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
