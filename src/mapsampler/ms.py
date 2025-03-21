import logging

from os                     import listdir, path
from psutil                 import virtual_memory
from shutil                 import rmtree
from subprocess             import run

from .ms_argparser           import MSArgumentParser
from .ms_filesplitter        import FileSplitter
from .ms_filter              import Filter
from .ms_logging             import logging_setup
from .ms_minimap2service     import Minimap2Service
       
class MS():
    
    def __init__(self):

        self.args         = MSArgumentParser().parse_args()
        self.mm2_service  = Minimap2Service(self.args)
        self.filter       = Filter(self.args)
        
        logging_setup(self.args.loglevel, "ms.log")

    def __enter__(self):
        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Removing tempdir on exit
        (when the programm terminates successfully or unsuccessfully)
        """
        
        rmtree(self.args.tempdir, ignore_errors=True)
    
    def ram_check(self):
        
        index_path    = path.join(self.args.tempdir,"reference.mm2idx")
        available_ram = virtual_memory().available
        index_ram     = path.getsize(index_path) * self.args.threads

        if index_ram > available_ram:
            raise Exception("Not enough RAM (Use less threads)")
        if index_ram > available_ram * 0.75:
            logging.warning("Probably not enough RAM (might crash)")

    def get_merge_file_paths(self, query_file)->list[str]:

        temp_files = listdir(self.args.tempdir)  
        query_base = path.basename(query_file)  
        
        filtered_files = [
            path.join(self.args.tempdir, f) 
            for f in temp_files 
            if f.startswith(f"filtered_{query_base}")
        ]
        
        return filtered_files
    
    def merge_files(self):
        for file in [self.args.query_left, self.args.query_right, self.args.query]:
            if file:
                merge_files = self.get_merge_file_paths(file)
                final_file  = file + ".ms"
                run(f"cat {' '.join(merge_files)} > {final_file}", shell=True)
            
def main():

    with MS() as ms:

        logging.info("Splitting query file(s) ...")
        FileSplitter.file_split(ms.args)

        logging.info("Indexing reference ...")
        ms.mm2_service.index()

        logging.info("Mapping ...")
        ms.ram_check()
        ms.mm2_service.map()
        
        logging.info("Start filtering ... ")
        ms.filter.filter()

        logging.info("Finalize")
        ms.merge_files()

        logging.info("+++++++++++++++++++++++++++++++++++++++")
        logging.info("Simon says: thanks for using mapsampler")
        logging.info("+++++++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    main()
    exit(0)
