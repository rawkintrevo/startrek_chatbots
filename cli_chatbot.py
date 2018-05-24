import tensorflow as tf


from nmt.nmt import attention_model
from nmt.nmt import gnmt_model
from nmt.nmt import model as nmt_model
from nmt.nmt import model_helper
from nmt.nmt.utils import misc_utils as utils
from nmt.nmt.utils import nmt_utils

from nmt.nmt.inference import load_data

model_dir = "/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/nmt/tmp/startrek_100_words_in_15_words_out_attention_model"
inf_data = load_data("/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/nmt/tmp/startrek_100_words_in_15_words_out/tst2012.in")
infer_data = ["RIKER : Captain , Romulan warbird decloaking . What should we do ? TROI : I heard there is a medical conference on Earth"]

with open("/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/nmt/tmp/startrek_100_words_in_15_words_out/vocab.in", 'r') as f:
    vocab_in = f.read().split("\n")

def load_infer_model(hparams,
              num_workers=1,
              scope=None):
    """Perform translation."""
    # if hparams.inference_indices:
    #     assert num_workers == 1

    if not hparams.attention:
        model_creator = nmt_model.Model
    elif hparams.attention_architecture == "standard":
        model_creator = attention_model.AttentionModel
    elif hparams.attention_architecture in ["gnmt", "gnmt_v2"]:
        model_creator = gnmt_model.GNMTModel
    else:
        raise ValueError("Unknown model architecture")
    infer_model = model_helper.create_infer_model(model_creator, hparams, scope)
    return infer_model




def _decode_inference_indices(model, sess, output_infer,
                              output_infer_summary_prefix,
                              inference_indices,
                              tgt_eos,
                              subword_option):
    """Decoding only a specific set of sentences."""
    utils.print_out("  decoding to output %s , num sents %d." %
                    (output_infer, len(inference_indices)))
    for decode_id in inference_indices:
        nmt_outputs, infer_summary = model.decode(sess)

        # get text translation
        assert nmt_outputs.shape[0] == 1
        translation = nmt_utils.get_translation(
            nmt_outputs,
            sent_id=0,
            tgt_eos=tgt_eos,
            subword_option=subword_option)

        if infer_summary is not None:  # Attention models
            image_file = output_infer_summary_prefix + str(decode_id) + ".png"
            utils.print_out("  save attention image to %s*" % image_file)
            image_summ = tf.Summary()
            image_summ.ParseFromString(infer_summary)
            with tf.gfile.GFile(image_file, mode="w") as img_f:
                img_f.write(image_summ.value[0].image.encoded_image_string)
        return translation

def decode_next_line(last_line):
    if isinstance(last_line, str):
        infer_data = [last_line]
    elif isinstance(last_line, list):
        infer_data = last_line
    else:
        print("last_line must be list or str")
        return 1
    with tf.Session(
            graph=infer_model.graph, config=utils.get_config_proto()) as sess:
        loaded_infer_model = model_helper.load_model(
            infer_model.model, ckpt, sess, "infer")
        sess.run(
            infer_model.iterator.initializer,
            feed_dict={
                infer_model.src_placeholder: infer_data,
                infer_model.batch_size_placeholder: hparams.infer_batch_size
            })
        # Decode
        utils.print_out("# Start decoding")
        if hparams.inference_indices:
            next_line = _decode_inference_indices(
                loaded_infer_model,
                sess,
                output_infer=output_infer,
                output_infer_summary_prefix=output_infer,
                inference_indices=hparams.inference_indices,
                tgt_eos=hparams.eos,
                subword_option=hparams.subword_option)
            utils.print_out(next_line)
        else:
            nmt_utils.decode_and_evaluate(
                "infer",
                loaded_infer_model,
                sess,
                output_infer,
                ref_file=None,
                metrics=hparams.metrics,
                subword_option=hparams.subword_option,
                beam_width=hparams.beam_width,
                tgt_eos=hparams.eos,
                num_translations_per_input=1) #hparams.num_translations_per_input)
            utils.print_out("uh oh...")
    return next_line

## inject line.

def concat_apostrophes(words):
    while "'" in words:
        i = words.index("'")
        if i == 0 or i == len(words) -1: # is ' first or last word? if so get another line (or the previous line)
            break
        contraction = words[i-1] + words[i] + words[i+1]
        del words[i+1]
        del words[i]
        words[i-1] = contraction
    return words

def split_apostrophes(string):
    return string.replace("'", " ' ")

def add_line_breaks(words):
    upperWs = [i for i in range(len(words)) if words[i].isupper() and len(words[i]) > 2]
    upperWs.reverse()
    for i in upperWs:
        words.insert(i, "\n")
    TWO_BREAK_FLAG = False
    if len(upperWs) > 1:
        TWO_BREAK_FLAG = True
    return words, TWO_BREAK_FLAG

def get_line(words):
    breaks = [i for i in range(len(words)) if words[i] == '\n']
    line = " ".join(words[breaks[0] + 1 : breaks[1]]) # + 1 to skip over \n
    return line

# for i in range(10):
#     next_line = decode_next_line(last_line)
#     full_output = full_output + " " + next_line.decode("utf-8")
#     last_line = " ".join((last_line + " " + next_line.decode("utf-8")).split()[-100:])
# print(full_output.replace(":", "\n"))

# for i in range(10):

def get_new_script_line(input):
    """

    :param input: Lass 100 Words of input
    :return:
    """
    all_lines = [input]
    new_lines = []
    output_line_searcher = ""
    while len(new_lines) < 1:
        output15 = decode_next_line(input).decode("utf-8")
        output_line_searcher = output_line_searcher + " " + output15
        words = output_line_searcher.split()
        words = concat_apostrophes(words)
        words, two_break_flag = add_line_breaks(words)
        if two_break_flag:
            while len([o for o in words if o == "\n"]) > 1:
                line = get_line(words)
                del_line = split_apostrophes(line)
                output_line_searcher = output_line_searcher.replace(del_line, "")
                new_lines.append(line)
                words = output_line_searcher.split()
                words = concat_apostrophes(words)
                words, two_break_flag = add_line_breaks(words)
            all_lines = all_lines + new_lines
        else:
            all_lines.append(output15)
        input = " ".join(" ".join(all_lines).split()[-100:]) ## Only draw input from "expressed" lines.
    return new_lines



hparams = utils.load_hparams(model_dir)
hparams.add_hparam('inference_indices', [0])
infer_model = load_infer_model(hparams)
ckpt = "/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/nmt/tmp/startrek_100_words_in_15_words_out_attention_model/translate.ckpt-200000"
output_infer = "/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/output.tmp"#io.StringIO()
import os
os.chdir("/home/rawkintrevo/gits/dl/tf_seq2seq_startrek/nmt")

# input = "TROI : Captain Picard , what do you think of Donald Trump ?"
# all_lines = [input]
#
# input = "TROI : Do you think President Trump is a qualified leader ?"
# all_lines.append(input)
#
# for i in range(2):
#     all_lines = all_lines + get_new_script_line(
#         " ".join(" ".join(all_lines).split()[-100:])  )






