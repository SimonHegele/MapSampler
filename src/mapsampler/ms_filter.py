import logging

from multiprocessing    import Pool
from os                 import listdir, path 
from typing             import Generator       

from .ms_sequencemappinqueue         import SequenceMappingQueue

from .file_services.utils            import get_read_reader
from .file_services.paf_file_service import PafFileService

class Filter():

    def __init__(self, args):

        self.args = args

    def mapping_passes(self, mapping: dict)->bool:

        if self.args.minimum_length  > mapping["alignment_length"]:
            return False
        if self.args.maximum_length  < mapping["alignment_length"]:
            return False
        if self.args.minimum_quality > mapping["alignment_quality"]:
            return False
        if self.args.maximum_quality < mapping["alignment_quality"]:
            return False
        if self.args.minimum_matches > mapping["matches"]:
            return False
        if self.args.maximum_matches < mapping["matches"]:
            return False
        
        return True
    
    def filter(self, query_path: str, mappings_path: str) -> Generator:

        queries  = get_read_reader(query_path).read(query_path)
        mappings = PafFileService.read(mappings_path)
        queue    = SequenceMappingQueue(queries, mappings)

        for query, query_mappings in queue.queue():
            if any([(self.mapping_passes(qm) ^ self.args.anti_filter) for qm in query_mappings]):
                yield query

    def process_split(self, args):
       
        query_path, mappings_path = args

        mappings_path = path.join(self.args.tempdir,mappings_path)
        filtered_path = path.join(self.args.tempdir,f"filtered_{query_path}")
        query_path    = path.join(self.args.tempdir,query_path)

        get_read_reader(query_path).write(filtered_path,
                                          self.filter(query_path,mappings_path))

    def get_files(self)->tuple[list,list]:
        """
        Retrieves the sorted lists with the query and mapping files for the multithreading

        Returns:
            tuple[list,list]: query and mapping files
        """
        mappings = sorted([f for f in listdir(self.args.tempdir) if f.endswith(".paf")])
        if self.args.query:
            queries       = sorted([f for f in listdir(self.args.tempdir)
                                    if f.startswith(path.basename(self.args.query))])
        else:
            queries_left  = sorted([f for f in listdir(self.args.tempdir)
                                    if f.startswith(path.basename(self.args.query_left))])
            queries_right = sorted([f for f in listdir(self.args.tempdir)
                                    if f.startswith(path.basename(self.args.query_right))])
            
            queries       = queries_left + queries_right
            mappings      = mappings + mappings

        return queries, mappings

    def process_all(self)->None:
        """
        Coordinates the filtering step using multiple threads in parallel
        """

        queries, mappings = self.get_files()

        logging.info(f"Starting {len(queries)} threads ({self.args.threads} at a time)")
        
        with Pool(processes=self.args.threads) as pool:
            pool.map(self.process_split,
                     zip(sorted(queries), mappings))
        
        logging.info("--- COMPLETED ---")
