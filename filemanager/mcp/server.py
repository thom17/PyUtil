import sys

from mcp.server.fastmcp import FastMCP
import clang

from filemanager.FolderManager import FolderManager

folder_manager =
units: dict[str, CUnit] = {}

@mcp.tool()
def parse(path: str) -> str:
    """두 수를 더합니다."""
    if not path in units:
        units[path] = CUnit.parse(path)
    return str(units[path])

#
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """이름에 따른 인사말을 반환합니다."""
#     return f"Hello, {name}!"
#
#
# # @mcp.tool()
# # def get_random_number(a: int, b: int) -> str:
# #     """0부터 100까지의 랜덤 숫자를 반환합니다."""
# #     import random
# #     return f"{a}~{b} -> {random.randint(a, b)}"
#
# def get_rand(a, b) -> int:
#     """0부터 100까지의 랜덤 숫자를 반환합니다."""
#     return random.randint(a, b)
#
#
# @mcp.tool()
# def get_random_number(a: int, b: int) -> int:
#     """0부터 100까지의 랜덤 숫자를 반환합니다."""
#     return get_rand(a, b)
#
#
# @mcp.tool()
# def dice(d: int, num: int = 1) -> str:
#     """주사위를 굴립니다."""
#     sb = ''
#     for i in range(num):
#         sb += f"{i + 1}번째 주사위 : {random.randint(1, d)}\n"
#     return sb
#
#
# @mcp.tool()
# def dice_graph(d: int, num: int = 10) -> str:
#     """주사위를 굴리고 결과를 그래프로 시각화합니다."""
#     results = []
#     result_text = ""
#
#     # 주사위를 굴려서 결과를 저장
#     for i in range(num):
#         roll = random.randint(1, d)
#         results.append(roll)
#         result_text += f"{i + 1}번째 주사위 : {roll}\n"
#
#     # 결과 빈도수 계산
#     counts = [0] * d
#     for roll in results:
#         counts[roll - 1] += 1
#
#     # 그래프 생성
#     plt.figure(figsize=(10, 6))
#     plt.bar(range(1, d + 1), counts)
#     plt.xlabel('주사위 값')
#     plt.ylabel('빈도')
#     plt.title(f'{d}면체 주사위 {num}회 굴림 결과')
#     plt.xticks(range(1, d + 1))
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
#
#     # 그래프를 이미지로 변환하고 Base64 인코딩
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     img_str = base64.b64encode(buffer.read()).decode('utf-8')
#     plt.close()
#
#     # 결과 구성: ASCII 아트 그래프와 상세 통계
#     stats = f"주사위 굴림 결과 통계:\n"
#     for i in range(1, d + 1):
#         stats += f"- {i}이(가) 나온 횟수: {counts[i - 1]}회\n"
#     stats += f"\n평균값: {sum(results) / len(results):.2f}"
#
#     # 이미지 URL 포함
#     img_html = f'<img src="data:image/png;base64,{img_str}" alt="주사위 분포 그래프">'
#
#     return result_text + "\n" + stats + "\n\n이미지 데이터: " + img_html
#
#
# @mcp.tool()
# def test_x(a: int, b: int) -> int:
#     """0부터 100까지의 랜덤 숫자를 반환합니다."""
#     return a ** b
#
#
# @mcp.tool()
# def get_time() -> str:
#     """현재 시간을 반환합니다."""
#     return 't = ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#
# # print(get_random_number(1, 10))
#
# @mcp.prompt()
# def test_prompt() -> str:
#     """Prompt를 테스트합니다."""
#     return f"위의 내용을 번역"

# 서버 실행
if __name__ == "__main__":
    mcp.run()