#!/usr/bin/python

# MicrobeCensus - estimation of average genome size from shotgun sequence data
# Copyright (C) 2013-2014 Stephen Nayfach
# Freely distributed under the GNU General Public License (GPLv3)

#######################################################################################
#   IMPORT LIBRARIES

try:
    import sys
except Exception:
	print ('Module "sys" not installed'); exit()
   
try:
    import os
except Exception:
    print ('Module "os" not installed'); exit()
          
try:
    import optparse
except Exception:
    print ('Module "optparse" not installed'); exit()

try:
    from ags_functions import *
except Exception:
	print ('Could not import ags_functions'); exit()

try:
	import platform
except Exception:
    print ('Module "platform" not installed'); exit()

#######################################################################################
#   CHECK OPERATING SYSTEM
operating_system = platform.system()
if operating_system not in ['Linux', 'Darwin']:
	sys.exit("Operating system '%s' not supported" % operating_system)

#######################################################################################
#   FILEPATHS TO SRC AND DATA FILES

main_dir    = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

src_dir     = os.path.join(main_dir, 'src')
bin_dir     = os.path.join(main_dir, 'bin')
data_dir    = os.path.join(main_dir, 'data')
p_rapsearch = os.path.join(bin_dir,  'rapsearch_'+operating_system+'_2.15')
p_db        = os.path.join(data_dir, 'rapdb_2.15')    
p_gene2fam  = os.path.join(data_dir, 'gene_fam.map')
p_gene2len  = os.path.join(data_dir, 'gene_len.map')
p_params    = os.path.join(data_dir, 'pars.map')
p_coeffs    = os.path.join(data_dir, 'coefficients.map')
p_weights   = os.path.join(data_dir, 'weights.map')
p_read_len  = os.path.join(data_dir, 'read_len.map')

# check that all paths to files are valid
for file in [p_rapsearch, p_db, p_gene2fam, p_gene2len, p_params, p_coeffs, p_weights, p_read_len]:
	if not os.path.isfile(file):
		print ("Could not locate the necessary input file:\n", file, "\n")
		print ("Make sure that the MicrobeCensus directory structure has not been modified")
		print ("and that program files have not been moved or renamed")
		sys.exit()

#######################################################################################
#   OPTIONS, ARGUMENTS, HELP                                                          
parser = optparse.OptionParser(usage = "Usage: microbe_census.py [-options] <seqfile> <outfile>")
parser.add_option("-n", dest="nreads",       default=1e6,     help="number of reads to use for AGS estimation (default = 1e6)")
parser.add_option("-l", dest="read_length",  default=None,    help="trim reads to this length (default = median read length)")
parser.add_option("-f", dest="file_type",    default=None,    help="file type: fasta or fastq (default = autodetect)")
parser.add_option("-c", dest="fastq_format", default=None,    help="fastq quality score encoding: [sanger, solexa, illumina] (default: autodetect)")
parser.add_option("-t", dest="threads",      default=1,       help="number of threads to use for database search (default = 1)")
parser.add_option("-q", dest="min_quality",  default=-5,      help="minimum base-level PHRED quality score: default = -5; no filtering")
parser.add_option("-m", dest="mean_quality", default=-5,      help="minimum read-level PHRED quality score: default = -5; no filtering")
parser.add_option("-d", dest="filter_dups",  default=False,   help="filter duplicate reads (default: False)", action='store_true')
parser.add_option("-u", dest="max_unknown",  default=100,     help="max percent of unknown bases: default = 100%; no filtering")
parser.add_option("-k", dest="keep_tmp",     default=False,   help="keep temporary files (default: False)", action='store_true')

#   parse options and arguments
(options, args) = parser.parse_args()
try:
	p_reads = args[0]
	p_out = args[1]
except Exception:
    print ("\nIncorrect number of command line arguments.")
    print ("\nUsage: microbe_census.py [-options] <seqfile> <outfile>")
    print ("For all options enter: microbe_census.py -h\n")
    sys.exit()

# check paths to p_reads and p_out are valid
if not os.path.isfile(p_reads):
	sys.exit("Could not locate path to <seqfile> %s" % p_reads)
try:
	open(p_out, 'w')
except Exception:
	sys.exit("Could open <outfile> %s " % p_out)

# set up and format options
p_wkdir = os.path.dirname(p_out)

read_length  = int(options.read_length) if options.read_length is not None else None
file_type    = options.file_type
nreads       = int(options.nreads) if options.nreads is not None else None
threads      = int(options.threads)
min_quality  = float(options.min_quality)
mean_quality = float(options.mean_quality)
fastq_format = options.fastq_format
filter_dups  = options.filter_dups
max_unknown  = float(options.max_unknown)/100
keep_tmp     = options.keep_tmp

#   check for valid values
read_lengths = read_list(p_read_len, header=False, dtype='int')
if read_length is not None and read_length not in read_lengths:
    sys.exit("Invalid read length: %s\nChoose a supported read length: %s" % (str(read_length), str(read_lengths)))

if file_type == "fasta" and any([min_quality > -5, mean_quality > -5, fastq_format is not None]):
    sys.exit("Quality filtering options are only available for FASTQ files")

if fastq_format not in ['sanger', 'solexa', 'illumina', None]:
    sys.exit("Invalid FASTQ quality encoding: %s\nChoose from: %s" % (fastq_format, "[sanger, solexa, illumina]"))

if file_type not in ['fasta', 'fastq', None]:
    sys.exit("Invalid file type: %s\nChoose a supported file type: %s" % (file_type, "[fasta, fastq]"))

if threads < 1:
    sys.exit("Invalid number of threads: %s\nMust be a positive integer." % str(threads))

if nreads is not None and nreads < 1:
    sys.exit("Invalid number of reads: %s\nMust be a positive integer." % str(nreads))

# autodetect certain parameters
if file_type is None:
	file_type = auto_detect_file_type(p_reads)
if read_length is None:
	read_length = auto_detect_read_length(p_reads, file_type, p_read_len) if read_length is None else read_length
if fastq_format is None and file_type == 'fastq':
	fastq_format = auto_detect_fastq_format(p_reads)

# print out copyright information
print ("\nMicrobeCensus - estimation of average genome size from shotgun sequence data")
print ("version 1.2.1 (November 2014); github.com/snayfach/MicrobeCensus")
print ("Copyright (C) 2013-2014 Stephen Nayfach")
print ("Freely distributed under the GNU General Public License (GPLv3)")

# print out parameters
print ("\n=============Parameters==============")
print ("Input metagenome: %s" % os.path.basename(p_reads))
print ("Output file: %s" % os.path.basename(p_out))
print ("Reads trimmed to: %s bp" % str(read_length))
print ("Maximum reads sampled: %s" % str(nreads))
print ("Threads to use for db search: %s" % str(threads))
print ("File format: %s" % file_type)
print ("Quality score encoding: %s" % (fastq_format if file_type == 'fastq' else 'NA'))
print ("Minimum base-level quality score: %s" % (str(min_quality) if file_type == 'fastq' else 'NA'))
print ("Minimum read-level quality score: %s" % (str(mean_quality) if file_type == 'fastq' else 'NA'))
print ("Maximum percent unknown bases/read: %s" % str(options.max_unknown))
print ("Filter duplicate reads: %s" % filter_dups)
print ("Keep temporary files: %s" % keep_tmp)

#######################################################################################
#   MAIN

print ("\n====Estimating Average Genome Size====")
# 1. Downsample nreads of read_length from seqfile;
#       -optionally detect FASTQ format, remove duplicates, and perform quality filtering
if file_type == 'fastq':
    p_sampled_reads, read_ids = process_fastq(p_reads, p_wkdir, nreads, read_length, mean_quality, min_quality, filter_dups, max_unknown, fastq_format, keep_tmp)
elif file_type == 'fasta':
    p_sampled_reads, read_ids = process_fasta(p_reads, p_wkdir, nreads, read_length, filter_dups, max_unknown, keep_tmp)

# 2. Search sampled reads against single-copy gene families using RAPsearch2
p_results, p_aln = search_seqs(p_sampled_reads, p_db, p_rapsearch, threads, keep_tmp, p_params)

# 3. Classify reads into gene families according to read length and family specific parameters
best_hits = classify_reads(p_results, p_aln, read_length, p_params, p_gene2fam, p_gene2len, keep_tmp, len(read_ids))

# 4. Count # of hits to each gene family
agg_hits = aggregate_hits(best_hits, read_length, p_params)

# 5. Predict average genome size:
#       -predict size using each of 30 gene models
#       -remove outlier predictions
#       -take a weighted average across remaining predictions
avg_size = pred_genome_size(agg_hits, len(read_ids), read_length, p_coeffs, p_weights)

# 6. Report results
write_results(p_out, len(read_ids), read_length, avg_size, keep_tmp, p_results, p_aln)
print ('\t%s bp' % str(round(avg_size, 2)))




