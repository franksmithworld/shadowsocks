#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging


class ServerStatus(object):
    def __init__(self, server):
        self.server = server
        self.latency = timedelta(seconds=10)
        self.last_time_detect_latency = datetime.now()
        self.last_read = datetime.now()
        self.last_write = datetime.now()
        self.last_failure = datetime.min
        self.score = 0


class HighAvailabilityStrategy(object):
    def __init__(self, config):
        self.config = config
        self.server_list = {}
        self.current_server = None
        self.reload_servers()

    def reload_servers(self):
        for server_dict in self.config['servers']:
            server = server_dict['server']
            if server not in self.server_list:
                self.server_list[server] = ServerStatus(server_dict)
        self.choose_new_server()

    def choose_new_server(self):
        old_server = self.current_server
        now = datetime.now()
        max_status = None
        for status in self.server_list.values():
            status.score = 100 * 1000 * min(5 * 60, (now - status.last_failure).seconds) \
                    - 2 * 5 * (min(2000, status.latency.milliseconds) / (1 + (now - status.last_time_detect_latency).seconds / 30 / 10)\
                    - 0.5 * 200 * min(5, (status.last_read - status.last_write).seconds))
            logging.debug("server: {0} latency:{1} score: {2}", status.server['server'], status.latency, status.score)
            if max_status is None or status.score > max_status.score:
                max_status = status
        if max_status:
            self.current_server = max_status.server
            logging.info('switching server from %s to %s', old_server['server'], self.current_server['server'])

    def get_a_server(self):
        self.choose_new_server()
        return self.current_server

    def update_latency(self, server, latency):
        logging.debug('latency: %s %d', server, latency.microseconds)
        if server in self.server_list:
            self.server_list[server].latency = latency
            self.server_list[server].last_time_detect_latency = datetime.now()

    def update_last_read(self, server):
        logging.debug('last read: %s', server)
        if server in self.server_list:
            self.server_list[server].last_read = datetime.now()

    def update_last_write(self, server):
        logging.debug('last write: %s', server)
        if server in self.server_list:
            self.server_list[server].last_write = datetime.now()

    def set_failure(self, server):
        logging.debug('last failure: %s', server)
        if server in self.server_list:
            self.server_list[server].last_failure = datetime.now()
