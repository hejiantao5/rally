# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
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

import collections

import mock

from rally import broker
from tests.unit import test


class BrokerTestCase(test.TestCase):

    def test__publisher(self):
        mock_publish = mock.MagicMock()
        mock_is_published = mock.MagicMock()
        queue = collections.deque()
        broker._publisher(mock_publish, queue, mock_is_published)
        mock_publish.assert_called_once_with(queue)
        mock_is_published.set.assert_called_once_with()

    def test__publisher_fails(self):
        mock_publish = mock.MagicMock(side_effect=Exception())
        mock_is_published = mock.MagicMock()
        queue = collections.deque()
        broker._publisher(mock_publish, queue, mock_is_published)
        mock_is_published.set.assert_called_once_with()

    def test__consumer(self):
        queue = collections.deque([1, 2, 3])
        mock_consume = mock.MagicMock()
        mock_is_published = mock.MagicMock()
        mock_is_published.isSet = mock.MagicMock(return_value=True)
        broker._consumer(mock_consume, queue, mock_is_published)
        self.assertEqual(3, mock_consume.call_count)
        self.assertEqual(0, len(queue))

    def test__consumer_cache(self):
        cache_keys_history = []

        def consume(cache, item):
            cache[item] = True
            cache_keys_history.append(cache.keys())

        queue = collections.deque([1, 2, 3])
        mock_is_published = mock.MagicMock()
        mock_is_published.isSet = mock.MagicMock(return_value=True)
        broker._consumer(consume, queue, mock_is_published)
        self.assertEqual([[1], [1, 2], [1, 2, 3]], cache_keys_history)

    def test__consumer_fails(self):
        queue = collections.deque([1, 2, 3])
        mock_consume = mock.MagicMock(side_effect=Exception())
        mock_is_published = mock.MagicMock()
        mock_is_published.isSet = mock.MagicMock(return_value=True)
        broker._consumer(mock_consume, queue, mock_is_published)
        self.assertEqual(0, len(queue))

    def test_run(self):

        def publish(queue):
            queue.append(1)
            queue.append(2)
            queue.append(3)

        consumed = set()

        def consume(cache, item):
            consumed.add(item)

        consumer_count = 2
        broker.run(publish, consume, consumer_count)
        self.assertEqual(set([1, 2, 3]), consumed)
