from argparse   import ArgumentParser
from datetime   import datetime
from math       import inf
from os         import mkdir, path

class MSArgumentParser(ArgumentParser):

    prog        =   "mapsampler"

    description =   """
                    Sampling of nucleotide sequences by mapping to a reference 
                    """
    
    def __init__(self) -> None:

        super().__init__(prog=self.prog, description=self.description)

        current_time = datetime.now().strftime("%dd%mm%Yy_%Hh%Mm%Ss")

        # Input files
        self.add_argument("reference",
                          help="Reference FASTA/FASTQ"
                          )
        self.add_argument("-q", "--query",
                          help="Query FASTA/FASTQ"
                          )
        self.add_argument("-ql", "--query_left",
                          help="Left query FASTA/FASTQ for paired-end Illumina short reads"
                          )
        self.add_argument("-qr", "--query_right",
                          help="Left query FASTA/FASTQ for paired-end Illumina short reads"
                          )
        
        # Output
        self.add_argument("-tmp", "--tempdir",
                          help="Path to empty to non-existing temporary directory",
                          default=f"ms_tmp_{current_time}"
                          )
        
        # Mapping
        self.add_argument("-m", "--mode",
                          help="Minimap2 mapping mode")
        
        # Filtering options
        self.add_argument("-a", "--anti_filter",
                          help="Anti filter: Select sequences without mappings meeting the criteria",
                          type=bool,
                          default=False
                          )
        self.add_argument("-minq", "--minimum_quality",
                          help="Minimum alignment quality",
                          type=int,
                          default=0
                          )
        self.add_argument("-maxq", "--maximum_quality",
                          help="Minimum alignment quality",
                          type=int,
                          default=inf
                          )
        self.add_argument("-minl", "--minimum_length",
                          help="Minimum alignment length",
                          type=int,
                          default=0
                          )
        self.add_argument("-maxl", "--maximum_length",
                          help="Minimum alignment length",
                          type=int,
                          default=inf
                          )
        self.add_argument("-minm", "--minimum_matches",
                          help="Minimum alignment length",
                          type=int,
                          default=0
                          )
        self.add_argument("-maxm", "--maximum_matches",
                          help="Minimum alignment length",
                          type=int,
                          default=inf
                          )
        
        # Others
        self.add_argument("-t", "--threads",
                          default=2,
                          type=int,
                          help="Number of threads CAUTION: Each thread loads the full reference!")
        self.add_argument("--loglevel",
                          type=str,
                          help="Choose loglevel. Mostly logs information about the progess",
                          default="info",
                          choices=["debug","info","warning","error","critical"])
        
    def parse_args(self):
        """
        Extends super().parse_args() by
        a) Checking input
        b) Creating outdir if needed
        """

        args = super().parse_args()

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
