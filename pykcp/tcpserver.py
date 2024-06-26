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


'''
TCP Server
'''

import tornado.tcpserver
from tornado.iostream import StreamClosedError
from tornado.ioloop import IOLoop
from tornado import gen
from kcp import KCP, IKCP_OVERHEAD, KCPSeg
from stream import KCPStream, IKCP_HANDSHAKE_KEYWORD

class TCPServer(tornado.tcpserver.TCPServer):
    '''
    TCP Server
    '''

    def __init__(self, ssl_options=None, max_buffer_size=None, read_chunk_size=None):
        tornado.tcpserver.TCPServer.__init__(self,\
                ssl_options=ssl_options,\
                max_buffer_size=max_buffer_size,\
                read_chunk_size=read_chunk_size)
        self.conv = 0
        self.kcpstream_dct = {}

    def handle_message(self, kcpstream, message):
        '''
        Handle message
        '''
        raise NotImplementedError()

    @gen.coroutine
    def handle_stream(self, stream, address):
        self.conv += 1
        kcpstream = KCPStream(KCP(self.conv, self.output), stream, address,\
                ioloop=IOLoop.current(), callback=self.handle_message)
        self.kcpstream_dct[self.conv] = kcpstream
        try:
            yield stream.write(b'%d\n\n\n' % self.conv)
            handshake = yield stream.read_until(IKCP_HANDSHAKE_KEYWORD)
            assert handshake == IKCP_HANDSHAKE_KEYWORD
            yield stream.write(IKCP_HANDSHAKE_KEYWORD)
            kcpstream.update()
            seg = None
            head = None
            while True:
                try:
                    if seg is None:
                        head = yield stream.read_bytes(IKCP_OVERHEAD)
                        seg = KCPSeg.decode(head)
                    else:
                        data = yield stream.read_bytes(seg.len)
                        kcpstream.kcp.input(head+data)
                        seg = None
                        head = None
                except StreamClosedError:
                    break
        finally:
            kcpstream.close()
            if kcpstream.kcp and kcpstream.kcp.conv:
                del self.kcpstream_dct[kcpstream.kcp.conv]


    @gen.coroutine
    def output(self, kcp, data):
        '''
        Output
        '''
        kcpstream = self.kcpstream_dct.get(kcp.conv)
        if kcpstream:
            yield kcpstream.stream.write(data)
