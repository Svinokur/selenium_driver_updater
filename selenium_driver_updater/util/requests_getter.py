from typing import Any, Optional, Tuple
import requests
import traceback
import logging
import json

import sys
import os

from requests.models import Response
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

class RequestsGetter():

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

    _headers = {'User-Agent': user_agent}

    @staticmethod
    def get_result_by_request(url : str, is_json : bool = False, return_text : bool = True, no_error_status_code : bool = False) -> Tuple[bool, str, int, Any]:
        """Gets html text and status_code from the specified url by get request

        Args:
            url (str)                   : Url which we will use for getting information
            cookies                     : Specific cookies for request
            is_json (bool)              : Transorm request.text to json or not. Defaults to False.
            no_error_status_code (bool) : If true, it will not return result False if status_code not equal to 200.

        Returns:
            Tuple[bool, str, int, Any]

            result_run (bool)   : True if successful, False otherwise.
            message_run (str)   : Empty string if successful, Non-empty string if error.
            status_code (int)   : Returns the status code of the given url
            request_text (str)  : Returns the html text of the given url

        Raises:
            Except: If unexpected error raised

        """

        result_run : bool = False
        message_run : str = ''
        status_code : int = 0
        request_text : str = ''
        request : Optional[Response] = None

        try:

            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'
            headers={'User-Agent': user_agent}
            request = requests.get(url=url, headers=headers)
            status_code = request.status_code

            if status_code != 200:
                
                if no_error_status_code:
                    return True, message_run, status_code, request.text
                
                else:
                    message_run = f'url: {url} status_code: {status_code} not equal 200 request_text: {request.text}'
                    logging.error(message_run)
                    return result_run, message_run, status_code, request.text

            if return_text:
                if is_json:
                    request_text = json.loads(request.text)
                else:
                    request_text = request.text

            result_run = True

        except json.decoder.JSONDecodeError:
            message_run = f'JSONDecodeError error: {str(traceback.format_exc())} request_text: {request.text}'
            logging.error(message_run)

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, status_code, request_text