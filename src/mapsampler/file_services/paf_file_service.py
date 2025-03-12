from typing import Generator

class PafFileService():

    sorted_keys = [ "query_name",
                    "query_length",
                    "query_start",
                    "query_end",
                    "strand",
                    "target_name",
                    "target_length",
                    "target_start",
                    "target_end",
                    "matches",
                    "alignment_length",
                    "alignment_quality"]
    
    numeric_keys = ["query_length",
                    "query_start",
                    "query_end",
                    "target_length",
                    "target_start",
                    "target_end",
                    "matches",
                    "alignment_length",
                    "alignment_quality"]

    @classmethod
    def parse_string(cls, line)->dict:

        d = {key: line.split("\t")[i] for i, key in enumerate(cls.sorted_keys)}

        for key in cls.numeric_keys:
            d[key] = int(d[key])

        d["format"] = "paf"

        return d
    
    @classmethod
    def parse_dict(cls, mapping: dict)->str:

        return "\t".join([mapping[key] for key in cls.sorted_keys])+"\n"

    @classmethod
    def read(cls, file)->Generator:

        with open(file, "r") as paf:

            for line in paf:

                yield cls.parse_string(line)

    @classmethod
    def write(cls, mappings: list[dict], file: str)->None:

        with open(file, "w") as paf:

            for mapping in mappings:

                paf.write(cls.parse_dict(mapping))