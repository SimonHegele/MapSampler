# MapSampler

Sampling of nucleotide sequences by mapping them to a reference using Minimap2.

\+ Time and memory efficient processing of arbitrarely large query files<br>
\-  Use of multithreading limited for large reference files.

## Installation

```
git clone https://www.github.com/SimonHegele/MapSampler
cd MapSampler
conda create -n mapsampler -f environment.yml
conda activate mapsampler
pip install .
```

## Usage

```
mapsampler -h
usage: mapsampler [-h] [-q QUERY] [-ql QUERY_LEFT] [-qr QUERY_RIGHT] [-tmp TEMPDIR] [-m MODE] [-a ANTI_FILTER] [-minq MINIMUM_QUALITY] [-maxq MAXIMUM_QUALITY] [-minl MINIMUM_LENGTH] [-maxl MAXIMUM_LENGTH]
                  [-minm MINIMUM_MATCHES] [-maxm MAXIMUM_MATCHES] [-t THREADS] [--loglevel {debug,info,warning,error,critical}]
                  reference

Sampling of nucleotide sequences by mapping to a reference

positional arguments:
  reference             Reference FASTA/FASTQ

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        Query FASTA/FASTQ
  -ql QUERY_LEFT, --query_left QUERY_LEFT
                        Left query FASTA/FASTQ for paired-end Illumina short reads
  -qr QUERY_RIGHT, --query_right QUERY_RIGHT
                        Left query FASTA/FASTQ for paired-end Illumina short reads
  -tmp TEMPDIR, --tempdir TEMPDIR
                        Path to empty to non-existing temporary directory
  -m MODE, --mode MODE  Minimap2 mapping mode
  -a ANTI_FILTER, --anti_filter ANTI_FILTER
                        Anti filter: Select sequences without mappings meeting the criteria
  -minq MINIMUM_QUALITY, --minimum_quality MINIMUM_QUALITY
                        Minimum alignment quality
  -maxq MAXIMUM_QUALITY, --maximum_quality MAXIMUM_QUALITY
                        Minimum alignment quality
  -minl MINIMUM_LENGTH, --minimum_length MINIMUM_LENGTH
                        Minimum alignment length
  -maxl MAXIMUM_LENGTH, --maximum_length MAXIMUM_LENGTH
                        Minimum alignment length
  -minm MINIMUM_MATCHES, --minimum_matches MINIMUM_MATCHES
                        Minimum alignment length
  -maxm MAXIMUM_MATCHES, --maximum_matches MAXIMUM_MATCHES
                        Minimum alignment length
  -t THREADS, --threads THREADS
                        Number of threads CAUTION: Each thread loads the full reference!
  --loglevel {debug,info,warning,error,critical}
                        Choose loglevel. Mostly logs information about the progess
```

### Output

<input.fasta/input.fastq>.ms

### Example:

`python ms.py -m sr -ql illumina_1.fastq -qr illumina_2.fastq -t 8 chr1_transcripts.fasta`

Input data:
- Query:     58,219,222 Illumina read-pairs pooled from six organs (brain, heart, kidney, liver, lung and stomach) of the mouse
- Reference: 7717 mouse chromosome 1 transcripts

Output data:
- 3,678,636 (~6,32%) of input Illumina read-pairs

Time (using 8 threads):
- real 7m24.496s
- user 36m32.332s

(Creating of a small scale benchmark data set for the evaluation of transcriptome assembly tools.)

<p align="center">
  <img src="ms_example.png" alt="Meine Bildunterschrift" width="500"/>
  <br>
  <em>Transcript counts estimated with Kallisto (https://github.com/pachterlab/kallisto) before and after filtering. Counts for chromosome 1 transcripts remain largely unchanged, counts for non-chromosome 1 transcripts are greatly reduced</em>
</p>

## How it works

1. **File splitting:**<br>
   Splitting the query file(s) with Seqtk (one part per thread) and moving them to the temporary directory.
2. **Index creation:**<br>
   Minimap2 indexing using the allowed number of threads.
3. **Mapping:**<br>
   All parts of the query file(s) are mapped in parallel with single-threaded Minimap2.
4. **Filtering:**<br>
   All parts of query files(s) and their corresponding mapping files are proccessed in parallel.
   Because of the use of single-threaded Minimap2, query sequences and their corresponding mappings appear in the same order in their respective files.
   This allows to only load one query sequence and its corresponding mappings at a time.
   If there is at least one mapping satisfying the specified requirements, the read is either accepted (default) or rejected (if --anti_filter is set).
   Accepted reads are written to separate files.
5. **File merging:**<br>
   The files with accepted sequences are merged into a dedicate files.
6. **Cleanup:**<br>
   The temporary directory is removed even if the run fails. (Exception: KeyboardInterrupt)

The use of single-threaded Minimap2 brings the huge advantage, that the memory footprint of the filtering step is independent on the size of the query file(s) and the time required for the filtering also only scales linear with the size of the query file(s). This allows to efficiently process arbitrarily large query file(s). On the downside, in the mapping step each thread has to load the Minimap2 index separately. Depending on the size of the reference file the MapSampler should therefore only be used with a limited number of threads as it might fail otherwise.
