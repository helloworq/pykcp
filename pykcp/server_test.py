#!/usr/bin/env python
#
# Copyright 2019 leenjewel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import
from tcpserver import TCPServer
from tornado.ioloop import IOLoop

class TestServer(TCPServer):

    def handle_message(self, kcpstream, msg):
         print('开始接收')
         with open(r'C:\Users\lei.zhou\Desktop\news.txt','wb+') as f:
             f.write(msg)
             print('write ok')
             print(len(msg))
             #kcpstream.send(b'>>>> %s' %msg)

    # def handle_message(self, kcpstream, msg):
    #     print('RECV: %s' % msg)
    #     kcpstream.send(b'>>>> %s' %msg)

if __name__ == '__main__':
    server = TestServer()
    server.listen(8888)
    IOLoop.current().start()
