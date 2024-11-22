import traceback
import logging
import sys
from time import time
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M')

class debug():
    _count_map = {}
    _counts = 0

    @staticmethod
    def print_info(error_msg: str = None):
        traceback.print_exc()
        logging.debug(f'{traceback.format_exc()}')
        if error_msg:
            print(error_msg)
            logging.debug(f'{error_msg}')
            

    @staticmethod
    def record_msg(error_msg: str, log_level=logging.debug):
        log_level(f'{error_msg}')

    @staticmethod
    def record_time_add(func):
        """
            用來計算函數所累積的時間判斷誰的影響最大

        Args:
            func (_type_): callable
        """
        def wrapper(*args, **kwargs):
            debug._counts += 1
            begin_time = time()
            result = func(*args, **kwargs)  
            end_time = time()            
            elapsed_time = end_time - begin_time
            countMap = debug._count_map
            if func.__name__ in countMap:
                countMap[func.__name__]['time'] += elapsed_time
                countMap[func.__name__]['use_count'] +=1
            else:
                countMap[func.__name__]= {}
                countMap[func.__name__].update({'time':elapsed_time})
                countMap[func.__name__].update({'use_count':1})
            
            print(countMap) 
            print('*'*120)
            return result
        return wrapper


def get_size(obj, seen=None):
    """Recursively finds the memory size of an object."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Mark this object as seen
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(vars(obj), seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])

    return size