# from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, config
#
# # Neo4j 데이터베이스 설정
# config.DATABASE_URL = "bolt://neo4j_manager:password@localhost:7687"  # Neo4j 연결 URL (본인의 설정에 맞게 수정)
#
#
# # 사용자(User) 노드 모델 정의
# class User(StructuredNode):
#     name = StringProperty(unique_index=True, required=True)
#     age = IntegerProperty(required=True)
#
#     # User-to-Post 관계 정의
#     posts = RelationshipTo("Post", "POSTED")
#
#
# # 게시물(Post) 노드 모델 정의
# class Post(StructuredNode):
#     title = StringProperty(unique_index=True, required=True)
#     content = StringProperty(required=True)
#
#     # Post-to-User 관계 정의
#     author = RelationshipFrom("User", "POSTED")
#
#
# # 예제 동작
# def main():
#     # 데이터 생성
#     user = User(name="Alice", age=30).save()
#     post = Post(title="First Post", content="This is my first post.").save()
#
#     # 관계 설정
#     user.posts.connect(post)
#
#     # 데이터 조회
#     retrieved_user = User.nodes.get(name="Alice")
#     print(f"User: {retrieved_user.name}, Age: {retrieved_user.age}")
#
#     for p in retrieved_user.posts:
#         print(f"Post: {p.title}, Content: {p.content}")
#
#     # 데이터 업데이트
#     retrieved_user.age = 31
#     retrieved_user.save()
#     print(f"Updated Age: {retrieved_user.age}")
#
#     # 데이터 삭제
#     retrieved_user.delete()  # 사용자를 삭제하면 연결된 관계도 삭제됨
#     post.delete()  # 게시물 개별 삭제
#
#
# if __name__ == "__main__":
#     main()
