from typing import List, Union

import requests
import requests_cache
import json
from os import getenv
from functools import wraps

from .exceptions import APIKeyError, InvalidDirectionError
from .vehicles import Bus, Train

_CACHE_EXPIRE = int(getenv('MARTA_CACHE_EXPIRE', 30))
_BASE_URL = 'https://developerservices.itsmarta.com:18096'
_TRAIN_PATH = '/itsmarta/railrealtimearrivals/developerservices/traindata'
_BUS_PATH = '/BRDRestService/RestBusRealTimeService/GetAllBus'
_BUS_ROUTE_PATH = '/BRDRestService/RestBusRealTimeService/GetBusByRoute/'

requests_cache.install_cache('marta_api_cache', backend='sqlite', expire_after=_CACHE_EXPIRE)

def require_api_key(func):
    """
    Decorator to ensure an API key is present
    """
    @wraps(func)
    def with_key(self, *args, **kwargs):
        if not kwargs.get('api_key'):
            if not self._api_key:
                raise APIKeyError()
            kwargs['api_key'] = self._api_key
        return func(self, *args, **kwargs)

    return with_key

def _convert_direction(user_direction: str, vehicle_type: str = 'bus') -> Union[str, None]:
    if not user_direction:
        return None
    if vehicle_type == 'bus':
        if user_direction.lower().startswith('n'):
            return 'Northbound'
        elif user_direction.lower().startswith('s'):
            return 'Southbound'
        elif user_direction.lower().startswith('e'):
            return 'Eastbound'
        elif user_direction.lower().startswith('w'):
            return 'Westbound'
        else:
            raise InvalidDirectionError(direction_provided=user_direction)
    elif vehicle_type == 'train':
        if user_direction.lower().startswith('n'):
            return 'N'
        elif user_direction.lower().startswith('s'):
            return 'S'
        elif user_direction.lower().startswith('e'):
            return 'E'
        elif user_direction.lower().startswith('w'):
            return 'W'
        else:
            raise InvalidDirectionError(direction_provided=user_direction)
    else:
        return user_direction


def _get_data(endpoint: str, api_key: str) -> dict:
    sep = '&' if '?' in endpoint else '?'
    url = f'{_BASE_URL}{endpoint}{sep}apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 401 or response.status_code == 403:
        raise APIKeyError(f'Your API key seems to be invalid. Try visiting {url}.')
    response.raise_for_status()
    return json.loads(response.text)

def _filter_response(response: dict, filters: dict) -> List[dict]:
    valid_items = []
    for item in response:
        valid = True
        for filter_key, filter_value in filters.items():
            if filter_value: # ignore if the filter value doesn't exist
                if not item.get(filter_key): # don't penalize if item doesn't have a filter_key
                    pass
                else:
                    item_val = str(item[filter_key]).strip().lower()
                    filt_val = str(filter_value).strip().lower()
                    if item_val != filt_val and filt_val not in item_val:
                        valid = False
        if valid:
            valid_items.append(item)
    return valid_items

class MARTA:
    def __init__(self, api_key: str = None):
        self._api_key = api_key
        if not api_key:
            self._api_key = getenv('MARTA_API_KEY')

    @require_api_key
    def get_trains(self,
                   line: str = None,
                   station: str = None,
                   destination: str = None,
                   direction: str = None,
                   api_key: str = None) -> List[Train]:
        """
        Query API for train information

        :param line: Train line identifier filter (red, gold, green, or blue)
        :type line: str, optional
        :param station: train station filter
        :type station: str, optional
        :param destination: destination filter
        :type destination: str, optional
        :param direction: Direction train is heading (N, S, E, or W)
        :param api_key: API key to override environment variable
        :type api_key: str, optional
        :return: list of Train objects
        :rtype: List[Train]
        """
        data = _get_data(endpoint=_TRAIN_PATH, api_key=api_key)
        filters = {
            'LINE': line,
            'DIRECTION': _convert_direction(user_direction=direction, vehicle_type='train'),
            'STATION': station,
            'DESTINATION': destination
        }
        matching_data = _filter_response(response=data, filters=filters)
        return [Train(t) for t in matching_data]

    @require_api_key
    def get_buses(self,
                  route: int = None,
                  stop_id: int = None,
                  vehicle_id: int = None,
                  time_point: str = None,
                  direction: str = None,
                  api_key: str = None) -> List[Bus]:
        """
        Query API for bus information
        :param route: route number
        :type route: int, optional
        :param stop_id: Bus stop ID
        :type stop_id: int, optional
        :param vehicle_id: Bus ID
        :type vehicle_id: int, optional
        :param time_point:
        :type time_point: str, optional
        :param direction: Bus direction (Northbound, Southbound, Westbound or Eastbound)
        :type direction: str, optional
        :param api_key: API key to override environment variable
        :type api_key: str, optional
        :return: list of Bus objects
        """

        if route:
            endpoint = f'{_BUS_ROUTE_PATH}/{route}'
        else:
            endpoint = f'{_BUS_PATH}'

        try:
            data = _get_data(endpoint=endpoint, api_key=api_key)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                print("\n[THONG BAO - XE BUYT] May chu REST API cho xe buyt (BRDRestService) da bi MARTA dong vinh vien (404 Not Found).")
                print("MARTA hien chi phat truc tiep du lieu xe buyt qua chuan GTFS-Realtime (Protocol Buffers).")
                return []
            raise
        filters = {
            'STOPID': stop_id,
            'VEHICLE': vehicle_id,
            'TIMEPOINT': time_point,
            'ROUTE': route,
            'DIRECTION': _convert_direction(user_direction=direction, vehicle_type='bus')
        }
        matching_data = _filter_response(response=data, filters=filters)
        return [Bus(b) for b in matching_data]


_default_instance = None

def _get_default_instance(api_key: str = None) -> MARTA:
    global _default_instance
    if _default_instance is None or (api_key and _default_instance._api_key != api_key):
        _default_instance = MARTA(api_key=api_key)
    return _default_instance

def get_trains(line: str = None,
               station: str = None,
               destination: str = None,
               direction: str = None,
               api_key: str = None) -> List[Train]:
    """
    Module-level wrapper for getting trains.
    """
    client = _get_default_instance(api_key=api_key)
    return client.get_trains(line=line, station=station, destination=destination, direction=direction, api_key=api_key)

def get_buses(route: int = None,
              stop_id: int = None,
              vehicle_id: int = None,
              time_point: str = None,
              direction: str = None,
              api_key: str = None) -> List[Bus]:
    """
    Module-level wrapper for getting buses.
    """
    client = _get_default_instance(api_key=api_key)
    return client.get_buses(route=route, stop_id=stop_id, vehicle_id=vehicle_id, time_point=time_point, direction=direction, api_key=api_key)
