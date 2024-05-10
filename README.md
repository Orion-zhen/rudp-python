# rudp-python

用Python实现可靠的UDP传输, 支持选择重传和回退N步(西安交通大学计网实验大作业)

## Functions

- [x] GBN协议
- [x] SR协议
- [x] 全双工传输
- [x] 命令行参数指定窗口大小, 超时时间, 发送文件等
- [x] 在广域网上运行

## Usage

在同一台电脑上, 运行`send.py`和`recv.py`可以使用GBN协议传输`send/mirror.jpg`文件

在本地和云服务器(我们使用阿里云服务器进行的测试)根据`frp/`中的配置文件运行frp后, 更改`dual.py`第21行的参数为你的服务器的公网IP, 然后在云服务器上运行`python dual.py -rm`, 在本地运行`python dual.py -l`即可使用GBN协议**全双工**地传输`send/mirror.jpg`文件

想要更换协议为SR, 可以指定参数`-p sr`

更多参数使用如下:

```shell
usage: send.py [-h] [--send-port SEND_PORT] [--target-host TARGET_HOST] [--target-port TARGET_PORT] [--recv-port RECV_PORT] [--proto {sr,gbn}] [--window-size WINDOW_SIZE] [--timeout TIMEOUT]
               [--file FILE] [--remote] [--local]

RUDP Server/Client configs

options:
  -h, --help            show this help message and exit
  --send-port SEND_PORT, -s SEND_PORT
                        发送方端口
  --target-host TARGET_HOST, -th TARGET_HOST
                        发送目标的IP
  --target-port TARGET_PORT, -tp TARGET_PORT
                        发送目标的端口
  --recv-port RECV_PORT, -r RECV_PORT
                        接收方端口
  --proto {sr,gbn}, -p {sr,gbn}
                        差错处理策略
  --window-size WINDOW_SIZE, -ws WINDOW_SIZE
                        窗口大小
  --timeout TIMEOUT, -to TIMEOUT
                        超时时间
  --file FILE, -f FILE  发送文件的路径
  --remote, -rm         在云服务器上选这个
  --local, -l           在本地运行
```
