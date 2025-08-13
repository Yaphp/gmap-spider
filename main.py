from config.config import API_URL
from common.session import get_session
from common.crawl import get_map_detail


def start():
    """
    主函数
    :return:
    """
    session = get_session()

    res = session.get(API_URL + "/api/crawl").json()

    print(res)

    if not res["success"]:
        print("获取待处理的全景图失败")
        exit()

    panoramas = res["data"]

    print("待处理的全景图数量：", len(panoramas))

    get_map_detail(session, panoramas)


if __name__ == '__main__':
    start()
