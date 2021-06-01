import sys
import click
import ipaddress
import threading
import subprocess
import time
from pathlib import Path


@click.group()
def commands():
    pass


@click.command()
@click.option("--network", "-n", required=True, type=str, help="network info")
@click.option("--save", "-s", is_flag=True, help="output save file to current path")
@click.option("--thread_num", "-t", type=int, default=10, help="thread numbers")
def scan(network, save, thread_num):
    scanner = Scanner(network, save, thread_num)
    scanner.start()


commands.add_command(scan)


def timer(func):
    def inner(*args, **kwargs):
        start_time = time.time()
        f = func(*args, **kwargs)
        end_time = time.time()
        print(f"扫描用时：{round(end_time-start_time, 2)}s")
        return f
    return inner


class Scanner(object):
    def __init__(self, network, save, thread_num):
        self.save = save
        self.network = ipaddress.IPv4Network(network)
        self.hosts = self.network.hosts()
        self.thread_num = thread_num
        self.alive = []

    def _is_alive(self):
        while True:
            try:
                ip = next(self.hosts)
                print(f"正在检测IP -> {ip}")
                if sys.platform == "win32":
                    command = f"ping -n 2 -w 3 {ip}"
                else:
                    command = f"ping -c 2 -w 3 {ip}"
                r_code, _ = subprocess.getstatusoutput(command)
                if not r_code:
                    self.alive.append(ip)
            except StopIteration:
                break

    @timer
    def start(self):
        ths = []
        for _ in range(self.thread_num):
            t = threading.Thread(target=self._is_alive)
            t.start()
            ths.append(t)

        for th in ths:
            th.join()

        print("扫描完成！！")
        if self.save:
            with open(Path(__file__).parent.joinpath("ip_alive.txt"), "w+", encoding="UTF-8") as fp:
                for ip in self.alive:
                    fp.write(f"{ip}\n")
        else:
            print(f"扫描结果：{self.alive}")


if __name__ == '__main__':
    commands()
