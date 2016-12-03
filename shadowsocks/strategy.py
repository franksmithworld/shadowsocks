#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime


class ServerStatus(object):
    def __init__(self, server):
        self.server = server
        self.latency = 10
        self.last_time_detect_latency = datetime.now()
        self.last_read = datetime.now()
        self.last_write = datetime.now()
        self.last_failure = datetime.min
        self.score = 0


class HighAvailabilityStrategy(object):
    def __init__(self, config):
        self.server_list = {}
        for server_dict in config['servers']:
            self.server_list[server_dict['server']] = server_dict
        self.current_server = self.server_list[config.get('chosen_index', 0)]

