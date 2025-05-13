"""
Module Name:    ms_minimap2service.py
Description:    Minimap2Service()
                - Calls Minimap2 to map query sequences from split input files to reference in parallel with each instance running on a single thread
Author:         Simon Hegele
Date:           2025-05-13
Version:        1.0
License:        GPL-3
"""

from multiprocessing    import Pool
from os                 import listdir, path
from subprocess         import run

class Minimap2Service():

    def __init__(self, args):

        self.args        = args
        self.index_path  = path.join(args.tempdir,"reference.mm2idx")
        self.mode_string = "" if args.mode == None else f"-x {args.mode}"
        
    def index(self):
        """
        Creates Minimap2 index in tempdir
        """

        run(f"minimap2 {self.mode_string} -t {self.args.threads} -d {self.index_path} {self.args.reference}".split(" "),
            check=True)
        
    def get_splitter_path(self, q, i):

        return path.join(self.args.tempdir,sorted([f for f in listdir(self.args.tempdir) if f.startswith(path.basename(q))])[i])
   
    def map_splitter(self, i):

        if self.args.query:
            reads    = self.get_splitter_path(self.args.query, i)
            print(reads)
            mappings = path.join(self.args.tempdir,f"mappings_{i}.paf")
            run(f"minimap2 {self.mode_string} -t {self.args.threads} -o {mappings} {self.index_path} {reads}".split(" "),
                 check=True)
        else:
            reads_left  = self.get_splitter_path(self.args.query_left, i)
            reads_right = self.get_splitter_path(self.args.query_right, i)
            mappings = path.join(self.args.tempdir,f"mappings_{i}.paf")
            path.join(self.args.tempdir,f"mappings_{i}.paf")
            run(f"minimap2 -x sr -t {self.args.threads} -o {mappings} {self.index_path} {reads_left} {reads_right}".split(" "),
                 check=True)
                    
    def map(self):    

        with Pool(processes=self.args.threads) as pool:
            pool.map(self.map_splitter, list(range(self.args.threads)))
