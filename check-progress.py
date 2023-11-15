import argparse
import subprocess as sp
from uuid import uuid4
import csv
import plotly.express as px
from collections import defaultdict
import pandas as pd
import webbrowser


argumentparser = argparse.ArgumentParser(description='Check progress of participants')
argumentparser.add_argument('--assigned-ips', type=str, help='Input file')
argumentparser.add_argument('--topic',type=str,help="topic to check progress on")

args = argumentparser.parse_args()

def get_progress(row):
    files = {
        'mapping': [
            '/home/user/data/tb/sample1.bam',
            '/home/user/data/tb/sample1.bam.bai',
            '/home/user/data/tb/sample2.bam',
            '/home/user/data/tb/sample2.bam.bai'
        ],
        "variants": [
            '/home/user/data/tb/variants/sample1.raw.vcf',
            '/home/user/data/tb/variants/sample2.raw.vcf',
            '/home/user/data/tb/variants/sample1.gatk.raw.vcf',
            '/home/user/data/tb/variants/sample2.gatk.raw.vcf',
            '/home/user/data/tb/variants/sample1.delly.vcf',
            '/home/user/data/tb/variants/sample2.delly.vcf',
        ],
        "assembly": [
            '/home/user/data/tb/sample1_asm/contigs.fasta',
            '/home/user/data/tb/sample1_asm/quast/report.txt',
            '/home/user/data/tb/sample1_asm/sample1_asm.crunch',
            '/home/user/data/tb/region.fastq',
            '/home/user/data/tb/region_assembly/contigs.fasta',
        ],
        "rnaseq": [
            '/home/user/data/transcriptomics/Mapping_Mtb/Mtb_L1.bam',
            '/home/user/data/transcriptomics/Mapping_Mtb/Mtb_L4.bam',
            '/home/user/data/transcriptomics/Mapping_Mtb/Mtb_L1_htseq_count.txt',
            '/home/user/data/transcriptomics/Mapping_Mtb/Mtb_L4_htseq_count.txt',
        ],
        "microbiome": [
            '/home/user/data/metagenomics/fastq_abs_paths',
            '/home/user/data/metagenomics/rooted_tree.qza',
            '/home/user/data/metagenomics/core-metrics-results/bray_curtis_emperor.qzv',
            '/home/user/data/metagenomics/taxa_barplot.qzv',
            '/home/user/data/metagenomics/beta_tests/bray_curtis_significance.qzv'
        ],
        "methylation": [
            '/home/user/data/'
        ],
        "third-gen":[
            '/home/user/data/nanopore_activity/basecalling/fastq/pass/pycoqc_results.html',
            '/home/user/data/nanopore_activity/mapping/sorted.bam'
            '/home/user/data/nanopore_activity/variant_calling/depth_statistics',
            '/home/user/data/nanopore_activity/phylogenetics/zika_all_aligned.fasta',
            '/home/user/data/nanopore_activity/phylogenetics/figtree/RAxML_bipartitions.zika_phylogeny'
        ],
        "phylo":[
            '/home/user/data/phylogenetics/RAxML_bipartitions.H1N1.flu.2009.ML.tre'
        ],
        "gwas":[
            '/home/user/data/gwas/MD.bed',
            '/home/user/data/gwas/MD.imiss-vs-het.pdf',
            '/home/user/data/gwas/MD.IBD-hist.pdf',
            '/home/user/data/gwas/clean.MD',
            '/home/user/data/gwas/clean.MD.lmiss.pdf',
            '/home/user/data/gwas/final.MD.assoc_mhplot.png'
        ]
    }

    files_found = set()
    for l in sp.Popen('ssh user@%s "find /home/user/data -exec du -hs {} \;"' % row['IP'],stdout=sp.PIPE,shell=True).stdout:
        files_found.add(l.decode().strip().split('\t')[1])

    progress = {}
    for p in files:
        position = 1
        for f in files[p]:
            if f not in files_found:
                position = files[p].index(f)
                break
        file_coverage = len(set(files[p]).intersection(files_found)) / len(files[p])
        position = position/len(files[p])
        progress[p] = {'name':row['Full Name'],'IP':row['IP'],"complete_position":position,'coverage':file_coverage}
    return progress

results = defaultdict(list)
for row in csv.DictReader(open(args.assigned_ips,encoding='utf-8-sig')):
    progress = get_progress(row)
    print(row['Linode'],row['IP'],progress)
    for key in progress:
        results[key].append(progress[key])

df = pd.DataFrame(results[args.topic])
fig = px.histogram(df, x="coverage",nbins=100,template="simple_white",title="Progress of participants")
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',  
    paper_bgcolor='rgba(0,0,0,0)', 
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(color='white'),  
    yaxis=dict(color='white'),  
    font=dict(color='white'),
    
)
fig.update_traces(marker=dict(
    line=dict(width=2, color='orange')
))
fig.update_traces(marker_color='darkred')
fig.write_html("progress.html")

with open("progress.html", "r") as file:
    html_content = file.read()

background_image_url = "url('https://github-production-user-asset-6210df.s3.amazonaws.com/100434056/282992812-179e1fc1-f7ab-407b-8035-dea5eb441d12.jpg')"

insertion_point = html_content.find('<body>') + len('<body>')

gif_html = """
<style>
body {
    background-image: """ + background_image_url + """;
    background-size: cover;
}
/* Additional styles */
</style>
<div style="display: flex; justify-content: center; align-items: center; height: 25vh; flex-direction: column; margin-bottom:50px">
    <div><img src="eye.png" alt="Blinking Eye" style="max-width: 100%; height: auto;"></div>
    <a href="https://www.fontspace.com/category/lord-of-the-rings"><img src="https://see.fontimg.com/api/renderfont4/51mgZ/eyJyIjoiZnMiLCJoIjo2NSwidyI6MTAwMCwiZnMiOjY1LCJmZ2MiOiIjQUEwNTA1IiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/QUxMIFNFRUlORyBFWUU/ringbearer-medium.png" alt="Lord of the Rings fonts"></a>
</div>"""

modified_html = html_content[:insertion_point] + gif_html + html_content[insertion_point:]

with open("progress.html", "w") as file:
    file.write(modified_html)



webbrowser.open('progress.html')

print(df[df['coverage'] == 0])


