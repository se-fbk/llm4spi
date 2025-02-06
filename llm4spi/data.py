from typing import Iterable, Dict
import gzip
import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
ZEROSHOT_DATA = os.path.join(ROOT, "..", "data", "specification_zeroshot_inputs.json")

def read_problems(data_file: str) -> Dict[str, Dict]:
    """
    Parses data file content to task dictionary
    """
    return {task["task_id"]: task for task in stream_json(data_file)}


def stream_json(filename: str) -> Iterable[Dict]:
    """
    Parses each the json-file describing the problems, and yields a list of problems,
    each is described as a dictionary.
    """
    with open(filename, "r") as fp:
        return json.load(fp)


def write_jsonl(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to a jsonl (json-lines) file.
    """
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    with open(filename, mode) as fp:
        for x in data:
            fp.write((json.dumps(x) + "\n").encode('utf-8'))

def write_json(filename: str, data: list[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to a json file.
    """
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    with open(filename, mode) as fp:
        fp.write((json.dumps(data,indent=3)).encode('utf-8'))

   