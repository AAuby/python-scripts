from client import HubFactory
from multiprocessing import Pool, Manager
from tools import run, random_hub_id, api, get_lamp_ids
from hubs import Hub
import fire


def initial_conf(hub_size, lamp_size):
    hubs = api.hubs or []
    if not hubs:
        # 初始化
        for _ in range(hub_size):
            while True:
                hid = random_hub_id()
                if hid not in hubs:
                    # 创建集控，绑定灯具
                    lamp_ids = get_lamp_ids(lamp_size)
                    hub = Hub(hid=hid, lamp_ids=lamp_ids)
                    hubs.append(hub)
                    break
        api.hubs = hubs
    return hubs


def main(pool_size=5, host="172.16.8.205", port=9999, hub_size=5, lamp_size=5):
    """
    程序入口
    :param pool_size: 进程池大小
    :param host: 服务端主机名
    :param port: 服务端端口
    :param hub_size: 集控个数
    :param lamp_size: 每个集控下的灯的个数
    :return:
    """

    # 初始化配置, 写入memcached缓存
    queue = Manager().Queue()
    hubs = initial_conf(hub_size, lamp_size)
    # 填充队列
    [queue.put(hub) for hub in hubs]
    p = Pool(pool_size)
    try:
        for i in range(pool_size):
            p.apply_async(run, args=(host, port, HubFactory(queue),))
        p.close()
        p.join()
        print("Done")
    except KeyboardInterrupt:
        p.terminate()


if __name__ == '__main__':
    fire.Fire(main)
