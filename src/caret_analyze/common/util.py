# Copyright 2021 Research Institute of Systems Planning, Inc.
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

from __future__ import annotations

import difflib

from logging import getLogger

import os

from statistics import mean
from typing import Any, Callable, Collection, Dict, Iterable, List, Optional, Tuple

from ..exceptions import ItemNotFoundError, MultipleItemFoundError

logger = getLogger(__name__)


class Util:

    @staticmethod
    def flatten(x: Iterable[Iterable[Any]]) -> List[Any]:
        import itertools

        return list(itertools.chain.from_iterable(x))

    @staticmethod
    def filter_items(f: Callable[[Any], bool], x: Optional[Iterable[Any]]) -> List[Any]:
        if x is None:
            return []
        return list(filter(f, x))

    @staticmethod
    def num_digit(i: int) -> int:
        return len(str(abs(i)))

    @staticmethod
    def ext(path: str) -> str:
        import os

        _, ext = os.path.splitext(path)
        return ext[1:]

    @staticmethod
    def find_one(condition: Callable[[Any], bool], items: Optional[Iterable[Any]]) -> Any:
        """
        Get a single item that matches the condition.

        Parameters
        ----------
        condition : Callable[[Any], bool]
        items : Optional[Iterable[Any]]

        Returns
        -------
        Any
            condition matched single item.

        Raises
        ------
        ItemNotFoundError
            Failed to find item that match the condition.
        MultipleItemFoundError
            Failed to identify item that match the condition.

        """
        if items is None:
            raise ItemNotFoundError('Failed find item.')

        filtered = Util.filter_items(condition, items)
        if len(filtered) == 0:
            raise ItemNotFoundError('Failed find item.')
        if len(filtered) >= 2:
            raise MultipleItemFoundError('Failed to identify item.')

        return filtered[0]

    @staticmethod
    def find_similar_one(
        target_name: str,
        items: Collection[Any],
        key: Callable[[Any], str] = lambda x: x,
        th: float = 0.6
    ) -> Any:

        similarity = 0.0
        for item in items:
            distance = difflib.SequenceMatcher(None, key(item), target_name).ratio()
            if (distance > similarity):
                similarity = distance
                most_similar_item = item

        assert 0.0 <= similarity <= 1.0
        if (similarity == 1.0):
            return most_similar_item
        elif (similarity > th):
            msg = 'Arguments may be wrong.'
            msg += f" Isn't it '{key(most_similar_item)}'?"
            raise ItemNotFoundError(msg)
        else:
            raise ItemNotFoundError('Failed find item.')

    @staticmethod
    def find_similar_one_multi_keys(
        target_names: Dict[str, str],
        items: Collection[Any],
        keys: Callable[[Any], Dict[str, str]] = lambda x: x,
        th: float = 0.6
    ) -> Any:
        max_similarity = 0.0
        for item in items:
            each_similarity = []
            keys_dict = keys(item)
            for target_name in target_names:
                if(keys_dict[target_name] is None):
                    each_similarity.append(0.0)
                    continue
                distance = difflib.SequenceMatcher(None,
                                                   keys_dict[target_name],
                                                   target_names[target_name]).ratio()
                each_similarity.append(distance)
            if (mean(each_similarity) > max_similarity):
                max_similarity = mean(each_similarity)
                most_similar_item = item

        assert 0.0 <= max_similarity <= 1.0
        if (max_similarity == 1.0):
            return most_similar_item
        elif (max_similarity > th):
            msg = 'Arguments may be wrong. '
            msg += "Aren't they bellow?\n"
            keys_dict = keys(most_similar_item)
            for k, v in keys_dict.items():
                msg += k + "='" + v + "'\n"
            raise ItemNotFoundError(msg)
        else:
            raise ItemNotFoundError('Failed find item.')

    @staticmethod
    def ns_to_ms(x: float) -> float:
        return x * 1.0e-6

    @staticmethod
    def get_ext(path: str) -> str:
        return os.path.basename(path).split('.')[-1]

    @staticmethod
    def to_ns_and_name(nodename: str) -> Tuple[str, str]:
        strs = nodename.split('/')
        ns = '/'.join(strs[:-1]) + '/'
        name = strs[-1]
        return ns, name
