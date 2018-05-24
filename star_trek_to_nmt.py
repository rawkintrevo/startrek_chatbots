import os
import string
import random

SCRIPT_DIR = "data/raw_scripts"

lead_type = "words" # options: words, lines
N_LINES_LEAD = 10
N_WORDS_LEAD = 100
N_WORDS_OUT = 15
N_OUT_LINES = 3
if lead_type == "lines":
    NMT_DIR = "nmt/tmp/startrek_%i_in_%i_out" % (N_LINES_LEAD, N_OUT_LINES)
if lead_type == "words":
    NMT_DIR = "nmt/tmp/startrek_%i_words_in_%i_words_out" % (N_WORDS_LEAD, N_WORDS_OUT)

all_lines = []
all_in_lines = []
all_out_lines = []
all_in_words = []
all_out_words = []
# real all lines from all files
print("Loading vocab from text files in:")
for d in os.listdir(SCRIPT_DIR):
    print(d)
    for fname in os.listdir("%s/%s" % (SCRIPT_DIR, d)):
        in_lines = []
        out_lines = []
        with open("%s/%s/%s" % (SCRIPT_DIR, d, fname), 'r') as f:
            data = f.read()
            # replace all punc with " punc "
            for p in string.punctuation:
                data = data.replace(p, " %s " % p)
            lines = [l.strip() for l in data.split("\n") if l.strip() != ""]
        if lead_type == "lines":
            in_lines = [" ".join(lines[i: i + N_LINES_LEAD]) for i in range(len(lines)-(N_LINES_LEAD + N_OUT_LINES - 1))]
            out_lines = [" ".join(lines[ i : i + N_OUT_LINES ]) for i in range(N_LINES_LEAD, len(lines) - N_OUT_LINES + 1)]
            all_in_lines.extend(in_lines)
            all_out_lines.extend(out_lines)
        if lead_type == "words":
            in_words = []
            out_words = []
            for i in range(N_LINES_LEAD + 1, len(lines) - N_OUT_LINES):
                in_lines = lines[i-N_LINES_LEAD: i]
                out_lines = lines[i: i + N_OUT_LINES]
                in_words = " ".join(" ".join(in_lines).split()[-N_WORDS_LEAD:])
                out_words = " ".join(" ".join(out_lines).split()[:N_WORDS_OUT])
                all_out_words.extend([out_words])
                all_in_words.extend([in_words])
        all_lines.extend(lines) #vocab is built off this, don't put it in if statement

print("files loaded")

# get vocab (write to .in and .out)
# line_batches = {
#     "in" : all_lines[:-1],
#     "out" : all_lines[1:]
# }
## Un comment above for doing single line in and out,
if lead_type == "words":
    all_in_lines = all_in_words
    all_out_lines = all_out_words

line_batches = {
    "in" : all_in_lines,
    "out": all_out_lines
}

files = {}
line_ct = 0
for fname in [f for f in os.listdir('nmt/tmp/nmt_data/') if f[-2:] == 'en']:
    with open("nmt/tmp/nmt_data/%s" % fname, "r") as f:
        files[fname] = len(f.read().split('\n'))
    if 'vocab' not in fname:
        line_ct += files[fname]
file_ps = {k : round(float(v)/line_ct,2) for k,v in files.items() if "vocab" not in k}
print("sizes calculated")

if not os.path.exists(NMT_DIR):
    os.mkdir(NMT_DIR)
    print("created dir: ", NMT_DIR)

c = 0
for k,v in file_ps.items():
    m = v / (1 - c)
    idx = random.sample(range(len(line_batches['in'])), round(len(line_batches['in']) * m))
    c += v
    inrows = [line_batches['in'][i] for i in idx]
    outrows = [line_batches['out'][i] for i in idx]
    idx.sort()
    idx.reverse()
    for i in idx:
        del line_batches['in'][i]
        del line_batches['out'][i]
    with open("%s/%s.in" % (NMT_DIR, k.split(".")[0]), "w") as f:
        f.write("\n".join(inrows))
    with open("%s/%s.out" % (NMT_DIR, k.split(".")[0]), "w") as f:
        f.write("\n".join(outrows))

if len(line_batches['in']) == 0 and len(line_batches['out']) == 0:
    print("files written successfully")

all_words = list(set([w for l in all_lines for w in l.split()]))
with open("%s/vocab.in" % (NMT_DIR), 'w') as f:
    f.write("\n".join(all_words))
with open("%s/vocab.out" % (NMT_DIR), 'w') as f:
    f.write("\n".join(all_words))

print("Copying to /tmp (don't delete this line, issue with NMT, will throw error on vocab if no in /tmp dir")
status = os.system("cp -rf %s /%s" % (NMT_DIR, "/".join(NMT_DIR.split("/")[1:])))
if status == 0:
    print("Success")
else: print("FAILED")
# run nmt model (BASIC)
"""
python3 -m nmt.nmt \
    --src=in --tgt=out \
    --vocab_prefix=/tmp/startrek/vocab  \
    --train_prefix=/tmp/startrek/train \
    --dev_prefix=/tmp/startrek/tst2012  \
    --test_prefix=/tmp/startrek/tst2013 \
    --out_dir=/tmp/startrek_model \
    --num_train_steps=12000 \
    --steps_per_stats=100 \
    --num_layers=2 \
    --num_units=128 \
    --dropout=0.2 \
    --metrics=bleu
"""

cli_str = """python3 -m nmt.nmt \
--attention=scaled_luong \
--src=in --tgt=out \
--vocab_prefix={0}/vocab  \
--train_prefix={0}/train \
--dev_prefix={0}/tst2012  \
--test_prefix={0}/tst2013 \
--out_dir={0}_attention_model \
--num_train_steps=200000 \
--steps_per_stats=100 \
--num_layers=4 \
--num_units=400 \
--dropout=0.2 \
--metrics=bleu \
--batch_size=256 \
--src_max_len={1} \
--tgt_max_len={2} \
--tgt_max_len_infer={2}
""".format("/".join(NMT_DIR.split("/")[1:]), N_WORDS_LEAD, N_WORDS_OUT)
print(cli_str)