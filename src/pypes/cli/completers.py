import os
from typing import List

from prompt_toolkit.completion import Completer, Completion


class FilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        possible_paths: List[str] = []
        head, tail = os.path.split(document.text)
        if os.path.exists(head):
            possible_paths += [x for x in os.listdir(head)]

        tail_len = len(tail)
        for path in possible_paths:
            if tail_len > 0:
                if path[0:tail_len] == tail:
                    yield Completion(path, start_position=-tail_len)
            else:
                yield Completion(path, start_position=0)
