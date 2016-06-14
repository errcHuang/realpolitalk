from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna
#parsing through fastas
for seq_record in SeqIO.parse('pfarq_sequences.fasta', 'fasta'):
    print(seq_record.id)
    print(seq_record.seq.alphabet)
    print(repr(seq_record.seq))
    print(len(seq_record))
"""
#parsing through one fasta
record = SeqIO.read('M34.contigs.fna', 'fasta')
print record
"""

