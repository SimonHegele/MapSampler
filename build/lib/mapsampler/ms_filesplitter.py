from subprocess import run

class FileSplitter():

    @staticmethod
    def file_split(args):
        """
        Splitting query files using seqtk and moving them to tempdir
        """
        for query_file in [args.query, args.query_left, args.query_right]:
            if query_file:
                run(f"seqtk split -n {args.threads} {query_file}.split {query_file}",
                    check=True,
                    shell=True)
                run(f"mv {query_file}.split* {args.tempdir}",
                    check=True,
                    shell=True)