# Copyright 2016 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""REST-like API base-class.

(Beginning of) the contract that all the resources must follow.
"""

# pylint: disable=invalid-name

import cherrypy
from oslo_log import log as logging

from arestor import config as arestor_config
from arestor.common import exception
from arestor.common import util as arestor_util

CONFIG = arestor_config.CONFIG
LOG = logging.getLogger(__name__)


class BaseAPI(object):

    """Contract class for all metadata providers."""

    _cp_config = {'tools.staticdir.on': False}

    exposed = True
    """Whether this application should be available for clients."""

    resources = None
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    def __init__(self, parent=None):
        self._parent = parent
        for raw_resource in self.resources or []:
            try:
                alias, resource = raw_resource
                setattr(self, alias, resource(self))
            except ValueError:
                LOG.error("Invalid resource %r provided.", raw_resource)

    @property
    def parent(self):
        """Return the object that contains the current resource."""
        return self._parent

    def GET(self):
        """ArestorV1 resource representation."""
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return "\n".join([endpoint for endpoint, _ in self.resources or []])


class Resource(object):

    """Contract class for all resources."""

    exposed = True
    """Whether this application should be available for clients."""

    def __init__(self, parent):
        self._parent = parent
        self._client_ip = cherrypy.request.remote.ip
        self._redis = arestor_util.RedisConnection()

    def _get_data(self, namespace, name, field=None):
        """Retrieve the required resource for the current client."""
        connection = self._redis.rcon
        key = "{namespace}/{name}/{user}".format(user=self.client_id,
                                                 namespace=namespace,
                                                 name=name)
        if not connection.exists(key):
            raise exception.NotFound(object=key, container="database")

        if field is None:
            return connection.hgetall(key)

        if not connection.hexists(key, field):
            raise exception.NotFound(object=field, container=key)

        return connection.hget(key, field)

    @property
    def parent(self):
        """Return the object that contains the current resource."""
        return self._parent

    @property
    def client_id(self):
        """The client IP address."""
        return self._client_ip
