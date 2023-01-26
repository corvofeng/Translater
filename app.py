import re
import nltk
from flask import Flask, request
from nltk.tokenize import sent_tokenize
from transformers import MarianMTModel, MarianTokenizer
nltk.download('punkt')


modchoice = "Helsinki-NLP/opus-mt-en-zh"
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def clean_text(text):
    text = text.encode("ascii", errors="ignore").decode(
        "ascii"
    )  # remove non-ascii, Chinese characters
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\n\n", " ", text)
    text = re.sub(r"\t", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"ADVERTISEMENT", " ", text)
    text = re.sub(
        r"Download our app or subscribe to our Telegram channel for the latest updates on the coronavirus outbreak: https://cna.asia/telegram",
        " ",
        text,
    )
    text = re.sub(
        r"Download our app or subscribe to our Telegram channel for the latest updates on the COVID-19 outbreak: https://cna.asia/telegram",
        " ",
        text,
    )
    text = text.strip(" ")
    text = re.sub(
        " +", " ", text
    ).strip()  # get rid of multiple spaces and replace with a single
    return text

def translate(text):
    input_text = clean_text(text)
    tokenizer = MarianTokenizer.from_pretrained(modchoice)
    model = MarianMTModel.from_pretrained(modchoice)
    if input_text is None or text == "":
        return ("Error",)
    translated = model.generate(
        **tokenizer.prepare_seq2seq_batch(
            sent_tokenize(input_text),
            truncation=True,
            padding="longest",
            return_tensors="pt"
        )
    )
    tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    return " ".join(tgt_text)


@app.route("/translate",  methods=['POST'])
def app_translate():
    req_data = request.get_json(force=True)
    text = req_data.get('text', '')

    return {
        'text': translate(text)
    }

# translate("Hello world. This is last time ")

# translate("""The project is called QueryStorm. It uses Roslyn to offer C# (and VB.NET) support in Excel, as an alternative to VBA. I've posted about it before, but a lot has changed since then so figured I'd share an update.
# The current version includes a host of new features, namely a C# debugger, support for NuGet packages, and the ability to publish Excel extensions to an "AppStore" (which is essentially a NuGet repository). The AppStore can be used by anyone with the (free) runtime component.
# Another great addition is the community license, which is a free license for individuals and small companies to use. It unlocks most features, but it isn't intended for companies with more than 5 employees or over $1M in annual revenue.
# I would love to hear your feedback and am happy to answer any technical questions about how QueryStorm is implemented.""")