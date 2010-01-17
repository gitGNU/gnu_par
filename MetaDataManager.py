#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2009, Zhang Initiative Research Unit,
Advance Science Institute, Riken
2-1 Hirosawa, Wako, Saitama 351-0198, Japan
If you use and like our software, please send us a postcard! ^^
---
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
---
"""

import logging, os, time

logger = logging.getLogger()
# log levels:
#  debug
#  info
#  warning
#  error
#  critical
#  exception

# criteria to cut a file into chunks
CHUNK_SIZE = 1024*1024

# How is described a file?
##########################
# metadata: <-- managed by MetaDataManager (only one per parallel.py server)
# =========
# - a name
# - a size (of the uncompressed file)
# - a creation time and date
#   [optionaly]
#   - a user
#   - a group
#   - permissions for UGO <-- NOTE: ACLs are fare better than UGO
# data: <-- managed by DataManager (one per parallel.py client,
#                                   ??? plus one for the server ???)
#                                   the server could be run on a cluster
#                                   frontend, some clusters don't like
#                                   that nodes use the frontend's
#                                   disk/network/CPU too heavily
# maybe we should have DataManagers only inside the cluster, and maybe
# we need a special mode (--mirror), which means this special DataManager
# must have all data listed by the MetaDataManager
# =====
# - a dictionary of chunks

class Metadata:

    def __init__(self, filename, dfs_path = None):
        self.was_created = False
        self.size = 0
        self.name = filename
        self.dfs_path = self.name
        self.creation_time = time.time()
        self.chunks = {}
        if dfs_path != None:
            self.dfs_path = dfs_path
        if os.path.isfile (self.name):
            try:
                self.size = os.path.getsize(self.name)
            except os.error:
                logger.exception ("can't get size of " + self.name)
        else:
            logger.error ("no file " + self.name)

# What is a chunk of Data?
##########################
# - chunks must be sortable (in order to retrieve how to recreate the file
#                            they belong to)
# - some data (compressed, we should be able to not use compression via
#              some option)
# - uncompressed data size
# - compressed data size
# - the list of nodes where this data is stored
#   on each node there is a path corresponding to the storage file
#   the storage backend is a GNU tar file containing only compressed (gzip -1)
#   files.
#   We'll think again later if we observe a bottleneck when writing massively
#   to it. Maybe then we will decide we need one backend per CPU to
#   parallelize writes on the same host (I/O load balancing).

class Data:

    def __init__(self, identifier, size, index):
        self.id = identifier
        self.size = size
        self.compressed_size = 0 # <=> uncompressed
        self.index = index
        self.nodes = []

# FBR: add the MetaDataManager to parallel.py for tests
