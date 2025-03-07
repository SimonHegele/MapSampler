from abc    import ABC, abstractmethod
from math   import inf
from typing import Generator

class FastaLikeFileService(ABC):

    @classmethod
    @abstractmethod
    def parse_string(cls, string: str)->dict:
        pass

    @classmethod
    @abstractmethod
    def parse_dict(cls, data: dict)->str:
        pass

    @classmethod
    def read(cls, file_path:str, only=inf)->Generator:
         
        string = ""
        done   = 0
        
        with open(file_path, "r") as f:

            for i, line in enumerate(f):

                if (line[0] == cls.separator) and (i > 0):
                    yield cls.parse_string(string)
                    done += 1
                    if done == only:
                        return
                    string = ""
                string += line

            yield cls.parse_string(string)

    @classmethod
    def write(cls, file_path: str, data: list[dict], mode="w", only=inf)->None:

        with open(file_path, mode) as file:
            for i, d in enumerate(data):
                if i < only:
                    file.writelines(cls.parse_dict(d))
                else:
                    return