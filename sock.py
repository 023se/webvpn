#!/usr/bin/env python
# coding=utf-8
import regex as re
import socket
import ssl
from threading import Thread

HOST = '127.0.0.1'
PORT = 7000

with open('./my.js', 'r', encoding="utf-8") as file:
    file_js_data = file.read()
    # # 去掉js文件中所有行注释
    # file_js_data = re.sub('//.*?\n','\n',file_js_data)
    file_js_data = file_js_data.replace(r'\w', r'\\w')

# socket 配置
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(100)


# 通信函数
def communication(conn):
    request = conn.recv(2048)
    # method = request.split(b' ', 1)[0]
    # method = method.decode()

    if len(request) == 0:
        conn.close()
        return
    src = request.split(b' ', 2)[1]
    src = src.decode()

    if src == '/favicon.ico':
        pattern = b'Referer: ?(\S*)'
        site_url = re.findall(pattern, request)[0]
        src = site_url.split(b'//', 1)[1].split(b'/', 1)[1]
        src = src.split(b'/')
        src = b'/' + b'/'.join([src[0], src[1], b'favicon.ico'])
        src = src.decode()
    protocol = src.split('/')[1]
    host = src.split('/')[2]
    hostname = host.split(':')[0]
    try:
        port = host.split(':')[1]
        port = int(port)
    except:
        # 如果没有端口号，默认为-1
        port = -1
    url = src.split('/')[3:]
    url = '/' + '/'.join(url)

    send_to_server_content = request.split(b' ', 2)
    send_to_server_content[1] = url.encode()
    send_to_server_content = b' '.join(send_to_server_content)

    send_to_server_content = re.sub(b'Host: ?(\\S*)', b'Host: ' + hostname.encode(), send_to_server_content, 1)

    # print(request.decode())
    # print('--------------------------')
    # print(send_to_server_content.decode())
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if protocol == 'http':
        tcp_socket.connect((hostname, 80 if port == -1 else port))
    elif protocol == 'https':
        tcp_socket = ssl.wrap_socket(tcp_socket)
        tcp_socket.connect((hostname, 443 if port == -1 else port))
    tcp_socket.send(send_to_server_content)
    data = b''
    first_send_flag = False
    replace_flag = False
    status_flag = False
    while True:
        re_data = tcp_socket.recv(4096)

        data += re_data
        if not status_flag and (b'\r\n\r\n' in data):
            status_flag = True
            try:
                pattern = b'Content-Length: ?(\d*)'
                content_length = re.findall(pattern, data)[0]
                content_length = int(content_length)
            except:
                # 没有Content-Length属性,给一个大数
                content_length = 9e100
        if status_flag:
            # 相应头接收完成
            if b'Content-Type: text/html' in data:
                # 是html文件类型
                if (not replace_flag) and (re.search(b'<html.*?>', data) is not None):
                    # 已经接收到<html>标签
                    replace_flag = True
                    content_type = re.findall(b'Content-Type: ?text/html', data)
                    js_str = b'\n<script type="text/javascript" charset="utf-8">' + file_js_data.encode() + b'</script>\n'
                    if len(content_type) != 0:
                        html_tag = re.findall(b'<html.*?>', data)
                        data = re.sub(html_tag[0], html_tag[0] + js_str, data, 1)
                        data = data.replace(b'Content-Length: ' + str(content_length).encode(),
                                            b'Content-Length: ' + str(content_length + len(js_str)).encode())
                        try:
                            pattern = b'Content-Length: ?(\d*)'
                            content_length = re.findall(pattern, data)[0]
                            content_length = int(content_length)
                        except:
                            # 没有Content-Length属性,给一个大数
                            content_length = 9e100
                if replace_flag and not first_send_flag:
                    first_send_flag = True
                    conn.send(data)
                elif first_send_flag:
                    conn.send(re_data)
                try:
                    result = data.split(b'\n\r\n',1)[1]
                except:
                    # 还没有接收到响应体
                    result = b''
                #里面有一个转译字符，所以减一
                if len(result) >= content_length-1:
                    break
            else:
                # 不是html文件类型
                try:
                    result = data.split(b'\n\r\n')[1]  # type:bytes
                except:
                    # 还没有接收到响应体
                    result = b''
                if not first_send_flag:
                    first_send_flag = True
                    conn.send(data)
                else:
                    conn.send(re_data)

                # 里面有一个转译字符，所以减一
                if len(result) >= content_length-1:
                    break
        if not re_data:
            break
    tcp_socket.close()

    conn.sendall(data)
    # close connection
    conn.close()


while True:
    # maximum number of requests waiting
    conn, addr = sock.accept()
    t = Thread(target=communication, args=(conn,))
    t.start()
