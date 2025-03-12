from . import fasta_like_file_service
from . import fasta_file_service
from . import fastq_file_service

def get_read_reader(read_file: str)->fasta_like_file_service.FastaLikeFileService:

    with open(read_file) as f:

        match f.readline()[0]:
            case ">":
                return fasta_file_service.FastaFileService()
            case "@":
                return fastq_file_service.FastqFileService()
            
def get_read_writer(read)->fasta_like_file_service.FastaLikeFileService:

    match read["file_type"]:
        case "fasta":
            return fasta_file_service.FastaFileService()
        case "fastq":
            return fastq_file_service.FastqFileService()