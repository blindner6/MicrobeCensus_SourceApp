SUMMARY
This software will rapidly and accurately estimate the average genome size (AGS) 
of a microbial community from metagenomic data. In short, AGS is estimated based 
on the rate (i.e. fraction of) reads in a metagenome are classified into a universal 
single copy gene family. Because these genes occur in nearly all Bacteria and 
Archaea, genome size is inversely proportional to this rate. Extensive shotgun DNA 
simulations were performed on a large set of phylogenetically diverse genomes to choose 
optimal alignment cutoffs for each gene family at each read length (50 to 500bp).  

We suggest that it is important to normalize for AGS when conducting comparative, functional
metagenomic analyses. For example, metagenomes with larger AGS will have an artificially
decreased abundance of housekeeping genes relative to a metagenomes with smaller AGS. To
normalize for AGS, simply multiply the abundance of genes by the AGS:

normalized abundance = observed abundance * AGS 

More information can be found in our publication, which should be in print soon.


INSTALLATION
Simply download our software package from github:

git clone git@github.com:snayfach/MicrobeCensus.git
--OR--
wget https://github.com/snayfach/MicrobeCensus/archive/master.zip

And add the path of the src directory to your PATH.


DEPENDENCIES
Python version 2.7; Our software has not yet been tested on other versions of Python
That's it! Necessary external libraries and binaries are included in our package.


USAGE
microbe_census [-options] <seqfile> <outfile> <nreads> <read_length>
For all options enter: microbe_census -h


EXAMPLES:
See the example directory.


RECOMMENDATION:
-filter duplicate reads using the -d flag; 
 be aware that this can consume large amounts of memory (>2G) when searching many reads (>20M)
-filter very low quality reads using -m 5 and -u 5
 note that these options are only available for FASTQ files
-limit <nreads> to less than 5e6.
 we found that accurate estimates of AGS can be made using as few at 500K reads.
-be sure to remove potential sources of contamination from your metagenome, including
 adaptor sequence and possibly host DNA (in the case of a host-associated metagenome)
-our software was primarily developed for use in microbial communities of Bacteria and Archaea;
 AGS may not be accurately estimated for communities composed of large amounts of Eukaryotes or Viruses












