#!/usr/local/env python 2.7

import subprocess, sys, os, multiprocessing, argparse
from argparse import RawTextHelpFormatter

"""performs quality trimming on .fq files in a given directory using trimgalore. Uses multiqc to create a comprehensive quality overview
path to target directory as well as number of processes should be given as arguments 1 and 2."""

def parse_arguments():
	man_description='%r\n\nperforms quality trimming on .fq files in a given directory using trimgalore. Uses multiqc to create a comprehensive quality overview.\n%r' % ('_'*80, '_'*80)
	parser=argparse.ArgumentParser(description=man_description.replace("'", ""), formatter_class=RawTextHelpFormatter)
	parser.add_argument('-d', '--target_dir', help='target directory containing fastq files', required=True)
	parser.add_argument('-p', '--processes', help='Number of processes to run the script', default=4, type=int)
	args=parser.parse_args()
	return args

def create_fastq_list(fq_root):
	fq_files=[]
	fq_count=0
	for file in os.listdir(fq_root):
		if file.endswith('.fastq') or file.endswith('.fq'):
			fq_count+=1
			fq_files.append(fq_root+'/'+file)
	print '%d fastq files identified in %s' % (fq_count, fq_root)

	#Identify files containing paired end reads and create a list of tuples
	fq_tuples=[]
	for fq_file in fq_files:
		if fq_file.rstrip('_1.fastq')+'_1.fastq' in fq_files and fq_file.rstrip('_1.fastq')+'_2.fastq' in fq_files:
			paired=str(fq_file.rstrip('_1.fastq')+'_1.fastq'+' '+fq_file.rstrip('_1.fastq')+'_2.fastq')
			fq_tuples.append(paired)
		elif fq_file.rstrip('_1.fq')+'_1.fq' in fq_files and fq_file.rstrip('_1.fq')+'_2.fq' in fq_files:
			paired=str(fq_file.rstrip('_1.fq')+'_1.fq'+' '+fq_file.rstrip('_1.fq')+'_2.fq')
			fq_tuples.append(paired)
		
		
	return fq_tuples


def perform_quality_analysis(element):
	
	fq_root=args.target_dir
	print 'starting quality trimming...'
	try:
		trimming_command='trim_galore %s --fastqc --paired --retain_unpaired --phred33 --length 20 -q 28 -e 0.1 -o %s' % (element, fq_root)
		subprocess.call(trimming_command, shell=True)
		print 'All sequences quality trimmed!'

	except Exception, e:
		print 'EXCEPTION: %s\nQuality trimming could not be performed, exiting.'
		sys.exit()
	
#####MAIN#####

args=parse_arguments()
if args.target_dir:

	fq_root=args.target_dir
	fq_files=create_fastq_list(fq_root)

	pool=multiprocessing.Pool(args.processes)
	pool.map(perform_quality_analysis, fq_files)
	pool.close()
	pool.join()

	print 'Creating multiqc report...'
	multiqc_command='multiqc -f -o %s %s' % (fq_root, fq_root)
	subprocess.call(multiqc_command, shell=True)

else:
	print 'Please give path to .fq files as script argument.'
	sys.exit()	
			
