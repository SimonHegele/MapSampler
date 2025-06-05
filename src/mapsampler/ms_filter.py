"""
Module Name:    ms_filesplitter.py
Description:    provides class Filter()
Author:         Simon Hegele
Date:           2025-05-13
Version:        1.0
License:        GPL-3
"""

import logging

from multiprocessing    import Manager, Pool
from os                 import listdir, path        

from .ms_sequencemappinqueue         import SequenceMappingQueue

from .file_services.utils            import get_read_reader
from .file_services.paf_file_service import PafFileService

class Filter():

    def __init__(self, args):

        for file in [args.query_left, args.query_right, args.query]:
            if file:
                self.file_service = get_read_reader(file)

        self.args = args

    def mapping_passes(self, mapping: dict)->bool:
        """
        Checks if a mapping satisfies the the criteria specified

        Args:
            mapping (dict): A mapping

        Returns:
            bool:   True    if the mapping satisfies the specified criteria,
                    False   else
        """

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
    
    def filter_split(self, args):
        """
        Reads sequences and corresponding mappings in parallel,
        accepts sequences with one or more mappings satisfying the specified criteria
        and writes them to a designated file.

        Args:
            args (tuple):   queries (str), mappings (str), thread (int)
                            queries:   A path to a file with nucleotide sequences (FASTA/FASTQ)
                            mappings:  A path to a file with corresponding mappings (PAF)
                            thread:    Index of the thread calling this function

        Returns:
            tuple: n_processed, n_filtered
        """

        query_file, mappings_file, thread= args

        logging.info("Thread {0:>3} started".format(thread))

        out_file = path.join(self.args.tempdir,f"filtered_{query_file}")
        queries  = self.file_service.read(path.join(self.args.tempdir,query_file))
        mappings = PafFileService.read(path.join(self.args.tempdir,mappings_file))
        filtered    = []

        for query, query_mappings in SequenceMappingQueue(queries, mappings).queue():
            if any([(self.mapping_passes(qm) ^ self.args.anti_filter) for qm in query_mappings]):
                filtered.append(query)
                if len(filtered) > 50:
                    self.file_service.write(out_file, filtered, mode="a")
                    
        self.file_service.write(out_file, filtered, mode="a")
        logging.info("Thread {0:>3} done".format(thread))

    def get_files(self)->tuple[list,list]:
        """
        Retrieves the sorted lists with the query and mapping files for the multithreadin

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

    def filter(self)->None:
        """
        Coordinates the filtering step using multiple threads in parallel
        """

        queries, mappings = self.get_files()

        logging.info("Starting {0} threads ({1} at a time)".format(len(queries),
                                                                       self.args.threads))
        
        with Pool(processes=self.args.threads) as pool:
            pool.map(   self.filter_split,
                        zip(sorted(queries), mappings, list(range(len(mappings)))))
        
        logging.info("--- COMPLETED ---")
