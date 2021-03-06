# Copyright 2015 - Savoir-Faire Linux inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

import httpretty

from surveil.tests.api import functionalTest


class TestStatusServices(functionalTest.FunctionalTest):

    def setUp(self):
        super(TestStatusServices, self).setUp()
        self.influxdb_response = json.dumps({
            "results": [
                {"series": [
                    {"name": "SERVICE_STATE",
                     "tags": {"host_name": "test_keystone",
                              "service_description":
                                  "Check KeyStone service."},
                     "columns": [
                         "time",
                         "last_check",
                         "last_state_change",
                         "output",
                         "state",
                         "state_type",
                         "acknowledged"
                     ],
                     "values":[
                         ["2015-04-19T18:20:34Z",
                          1.429467634e+09,
                          1.429467636632134e+09,
                          ("There was no suitable "
                           "authentication url for this request"),
                          3,
                          "SOFT",
                          0]
                     ]},
                    {"name": "SERVICE_STATE",
                     "tags": {"host_name": "ws-arbiter",
                              "service_description": "check-ws-arbiter"},
                     "columns": [
                         "time",
                         "last_check",
                         "last_state_change",
                         "output",
                         "state",
                         "state_type",
                         "acknowledged"
                     ],
                     "values":[
                         ["2015-04-19T18:20:33Z",
                          1.429467633e+09,
                          1.429467635629833e+09,
                          "TCP OK - 0.000 second response time on port 7760",
                          0,
                          "HARD",
                          0]
                     ]}
                ]}
            ]
        })

    @httpretty.activate
    def test_get_all_services(self):
        httpretty.register_uri(httpretty.GET,
                               "http://influxdb:8086/query",
                               body=self.influxdb_response)

        response = self.get("/v2/status/services")

        expected = [
            {'description': 'Check KeyStone service.',
             'last_state_change': 1429467636,
             'plugin_output':
                 'There was no suitable authentication url for this request',
             'last_check': 1429467634,
             'state': 3,
             "acknowledged": 0,
             'host_name': 'test_keystone',
             'service_description': 'Check KeyStone service.'},
            {'description': 'check-ws-arbiter',
             'last_state_change': 1429467635,
             'plugin_output':
                 'TCP OK - 0.000 second response time on port 7760',
             'last_check': 1429467633,
             'state': 0,
             "acknowledged": 0,
             'host_name': 'ws-arbiter',
             'service_description': 'check-ws-arbiter'}
        ]

        self.assertEqual(json.loads(response.body), expected)

        self.assertEqual(
            httpretty.last_request().querystring['q'],
            ["SELECT * FROM SERVICE_STATE GROUP BY host_name,"
             " service_description "
             "ORDER BY time DESC "
             "LIMIT 1"]
        )

    @httpretty.activate
    def test_query_services(self):
        influxdb_response = json.dumps({
            "results": [
                {"series": [
                    {"name": "SERVICE_STATE",
                     "tags": {"host_name": "test_keystone",
                              "service_description":
                                  "Check KeyStone service."},
                     "columns": [
                         "time",
                         "last_check",
                         "last_state_change",
                         "output",
                         "state",
                         "state_type",
                         "acknowledged"
                     ],
                     "values":[
                         ["2015-04-19T18:20:34Z",
                          1.429467634e+09,
                          1.429467636632134e+09,
                          ("There was no suitable "
                           "authentication url for this request"),
                          3,
                          "SOFT",
                          0]
                     ]}
                ]}
            ]
        })

        httpretty.register_uri(httpretty.GET,
                               "http://influxdb:8086/query",
                               body=influxdb_response)

        query = {
            'fields': json.dumps(['host_name', 'service_description']),
            'filters': json.dumps({
                "isnot": {
                    "host_name": ['ws-arbiter'],
                },
                "is": {
                    "service_description": ["Check KeyStone service."]
                }
            })
        }

        response = self.post_json("/v2/status/services", params=query)

        expected = [
            {'host_name': 'test_keystone',
             'service_description': 'Check KeyStone service.'}
        ]

        self.assertEqual(json.loads(response.body), expected)
