"""
Module Name:    ms_argumentparser.py
Description:    Provides class MSArgumentParser(ArgumentParser)
                - Arguments for MapSampler added on initialization
                - Extended parse_args() to check input
Author:         Simon Hegele
Date:           2025-05-13
Version:        1.0
License:        GPL-3
"""

from argparse   import ArgumentParser
from datetime   import datetime
from math       import inf
from os         import mkdir, path

class MSArgumentParser(ArgumentParser):

    prog        =   "mapsampler"

    description =   """
                    Sampling of nucleotide sequences by mapping to a reference 
                    """

    version     = "v1.0"
    
    def __init__(self) -> None:

        super().__init__(prog=self.prog, description=self.description)

        current_time = datetime.now().strftime("%dd%mm%Yy_%Hh%Mm%Ss")

        self.add_argument("reference",
                          help="Reference FASTA/FASTQ"
                          )
        
        grp1 = self.add_argument_group("Query-file(s)")
        grp1.add_argument("-q", "--query",
                          metavar="",
                          help="Query FASTA/FASTQ"
                          )
        grp1.add_argument("-ql", "--query_left",
                          metavar="",
                          help="Left query FASTA/FASTQ for paired-end Illumina short reads"
                          )
        grp1.add_argument("-qr", "--query_right",
                          metavar="",
                          help="Right query FASTA/FASTQ for paired-end Illumina short reads"
                          )
        
        grp2 = self.add_argument_group("Mapping")
        grp2.add_argument("-m", "--mode",
                          metavar="",
                          help="Minimap2 mapping mode")
        
        grp3 = self.add_argument_group("Filtering")
        grp3.add_argument("-a", "--anti_filter",
                          help="Anti filter: Select sequences without mappings meeting the criteria",
                          type=bool,
                          metavar="",
                          default=False
                          )
        grp3.add_argument("-minq", "--minimum_quality",
                          help="Minimum alignment quality",
                          type=int,
                          metavar="",
                          default=0
                          )
        grp3.add_argument("-maxq", "--maximum_quality",
                          help="Minimum alignment quality",
                          type=int,
                          metavar="",
                          default=inf
                          )
        grp3.add_argument("-minl", "--minimum_length",
                          help="Minimum alignment length",
                          type=int,
                          metavar="",
                          default=0
                          )
        grp3.add_argument("-maxl", "--maximum_length",
                          help="Minimum alignment length",
                          metavar="",
                          type=int,
                          default=inf
                          )
        grp3.add_argument("-minm", "--minimum_matches",
                          help="Minimum alignment length",
                          type=int,
                          metavar="",
                          default=0
                          )
        grp3.add_argument("-maxm", "--maximum_matches",
                          help="Minimum alignment length",
                          type=int,
                          metavar="",
                          default=inf
                          )
        
        # Others
        grp4 = self.add_argument_group("Others")
        grp4.add_argument("-t", "--threads",
                          default=8,
                          type=int,
                          metavar="",
                          help="Number of threads CAUTION: Each thread loads the full reference!")
        grp4.add_argument("-tmp", "--tempdir",
                          metavar="",
                          help="Path to empty to non-existing temporary directory",
                          default=f"ms_tmp_{current_time}"
                          )
        grp4.add_argument("--loglevel",
                          type=str,
                          help="Choose loglevel. Mostly logs information about the progess",
                          default="info",
                          metavar="",
                          choices=["debug","info","warning","error","critical"])
        grp4 .add_argument("-v", "--version",
                          help="print version",
                          type=bool,
                          metavar="",
                          default=False
                          )
        
    def parse_args(self):
        """
        Extends super().parse_args() by
        a) Checking input
        b) Creating outdir if needed
        """

        args = super().parse_args()

        if args.version:
            print(self.version)
            exit(0)

        # Input files
        if args.query and (args.query_left or args.query_right):
            raise Exception("Use either unpaired or paired query, not both")
        if bool(args.query_left) ^ bool(args.query_right):
            raise Exception("Must specify both query_left and query_right for paired query")

        # Filtering options
        if args.minimum_length > args.maximum_length:
            raise Exception("minimum_length can't be greater than maximum_length")
        if args.minimum_quality > args.maximum_quality:
            raise Exception("minimum_quality can't be greater than maximum_quality")
        if args.minimum_matches > args.maximum_matches:
            raise Exception("minimum_matches can't be greater than maximum_matches")

        # Output
        if not path.isdir(args.tempdir):
            mkdir(args.tempdir)
        elif path.listdir(args.tempdir):
            raise Exception("Temporary directory not empty")
        
        # Mapping
        if (args.query_left and args.query_right) and not args.mode == "sr":
            raise Exception("Must specify mode sr for paired queries")
                
        return args
