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

# pylint: disable=invalid-name

"""Arestor API endpoint for OpenStack Mocked Metadata."""

from oslo_log import log as logging

from arestor.api import base as base_api


LOG = logging.getLogger(__name__)


class _Content(base_api.Resource):

    """Content resource for the OpenStack Endpoint."""

    exposed = True

    def GET(self):
        """The representation of the content resource."""
        pass


class _MetadataResource(base_api.Resource):

    """Metadata resource for OpenStack Endpoint."""

    exposed = True

    def GET(self):
        """The representation of the metadata resource."""
        pass


class _UserdataResource(base_api.Resource):

    exposed = True

    """Userdata resource for OpenStack Endpoint."""

    def GET(self):
        """The representation of userdata resource."""
        pass


class _PasswordResource(base_api.Resource):

    exposed = True

    """Password resource for OpenStack Endpoint."""

    def GET(self):
        """The representation of password resource."""
        pass

    def POST(self):
        """Overwrite the password resource."""
        pass


class _LatestVersion(base_api.BaseAPI):

    """Container for all the resources from the latest version of the API."""

    exposed = True
    resources = [
        ("user_data", _UserdataResource),
        ("meta_data.json", _MetadataResource),
    ]


class _LegacyVersion(base_api.BaseAPI):

    """Containe for all the resources from the legacy version of the API."""

    exposed = True
    resources = [
        ("password", _PasswordResource),
    ]


class OpenStackEndpoint(base_api.BaseAPI):

    """Arestor API endpoint for OpenStack Mocked Metadata."""

    resources = [
        ("2013-04-04", _LegacyVersion),
        ("latest", _LatestVersion),
        ("content", _Content),
    ]
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    exposed = True
    """Whether this application should be available for clients."""

    def __getattr__(self, name):
        """Handle for invalid resource name or alias."""

        # Note(alexcoman): The cherrypy MethodDispatcher will replace the
        # `-` from the resource / endpoint name with `_`. In order to avoid
        # any problems we will try to avoid this scenario.
        if "_" in name:
            return self.__dict__.get(name.replace("_", "-"))

        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))
