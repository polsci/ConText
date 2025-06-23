from conc.corpus import Corpus
from conc.conc import Conc
from conc.corpora import list_corpora
from conc.core import set_logger_state
from flask import Flask, render_template, redirect, url_for, request, make_response

# TODO:
# show settings on load if not set
# paging
# links to context
# formatting of tables 
# handle escaping
# set / load corpus and reference corpus
# set defaults for various reports
# low priority - update title on url changes
# low priority - do loading thing - hx-indicator

# conc result - implement summary value so can pass to context

app = Flask(__name__)

save_path = '/home/geoff/data/conc-test-corpora/'

global corpus
global reference_corpus
global conc

corpus = Corpus().load(f'{save_path}garden-party.corpus')
reference_corpus = Corpus().load(f'{save_path}brown.corpus')
conc = Conc(corpus)

conc.set_reference_corpus(reference_corpus)
#corpora.get_column('corpus').to_list()

def _get_default():
    return render_template("context-default.html")

def _get_query(search, order):
    return render_template("context-query.html", concordance_url = url_for('concordance', search=search, order=order), clusters_url = url_for('clusters', search=search, order=order))

def _get_query_html(search_string, order_string):
    context_left = '<h2>Clusters</h2>' + conc.ngrams(search_string, ngram_length = None).to_html() 
    context_right = '<h2>Concordance</h2>'
    
    context_right += f'<button id="context-chart-button" hx-target="#context-right" hx-post="/concordanceplot/{search_string}/{order_string}"><span>Concordance Plot</span></button>'
    context_right += conc.concordance(search_string, context_length = 20, order = order_string).to_html()
    context_full = ''
    return render_template("context.html", 
                               context_left=context_left, 
                               context_right=context_right, 
                               context_full=context_full,
                               context_data_title=f'ConText : {search_string} ({order_string})'
                               )

def _get_concordanceplot_html(search, order):
    context = '<h2>Concordance Plot</h2>'
    context += f'<nav id="context-right-nav"><button id="context-table-button" hx-target="#context-right" hx-get="/concordance/{search}/{order}"><span>Concordance</span></button><button id="context-options-button"><span>Options</span></button></nav>'
    context += conc.concordance_plot(search).to_html()
    return context

@app.route("/")
def home():
    search_string = ''
    order_string = '1R2R3R'
    context = _get_default()
    return render_template("index.html", search = search_string, order=order_string, context=context)

@app.route("/default_home")
def default_home():
    context = _get_default()
    response_url = url_for('home')
    response = make_response(context)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    return response

@app.route('/corpus-info', methods=['POST'])
def corpus_info():
    return render_template("corpus-info.html", title = 'Corpus Information', table = corpus.report().to_html())

@app.route('/keywords')
def keywords():
    return '<h2>Keywords</h2>' + conc.keywords(min_document_frequency_reference = 5, show_document_frequency = True).to_html()

@app.route('/collocates/<search>/<order>')
def collocates(search, order):
    return '<h2>Collocates</h2>' + conc.collocates(search).to_html() 

@app.route('/clusters/<search>/<order>')
def clusters(search, order):
    return '<h2>Clusters</h2>' + conc.ngrams(search, ngram_length = None).to_html() 

@app.route('/concordance/<search>/<order>')
def concordance(search, order):
    return '<h2>Concordance</h2>' + f'<nav id="context-right-nav"><button id="context-chart-button" hx-target="#context-right" hx-get="/concordanceplot/{search}/{order}"><span>Concordance Plot</span></button><button id="context-options-button"><span>Options</span></button></nav>' + conc.concordance(search, context_length = 20, order = order).to_html()

@app.route("/concordanceplot/<search>/<order>")
def concordanceplot(search, order):
    # TODO escape search and order
    context = _get_concordanceplot_html(search, order)
    return context

@app.route("/query/<search>/<order>")
def query(search, order):
    # TODO escape search and order
    context_html = _get_query(search, order)
    return render_template("index.html", search = search, order=order, context=context_html)

@app.route("/query_context", methods=['POST'])
def query_context():
    search = request.form.get('search') # TODO escape search and order
    order = request.form.get('order')
    context = _get_query(search, order)
    response = make_response(context)
    response_url = url_for('query', search=search, order=order)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    return response

@app.route("/detail", methods=['GET'])
def detail():
    #corpus_info = f"{corpus.word_token_count:,} word tokens ({corpus.word_token_count/1_000_000:.2f} million tokens), {corpus.document_count:,} documents loaded"
    corpus_info = f"Word tokens: {corpus.word_token_count/1_000_000:.2f} million &bull; Documents: {corpus.document_count:,}"
    return render_template("detail.html", 
                           corpus_name=corpus.name, 
                           corpus_info=corpus_info)

@app.route("/corpus_select", methods=['POST'])
@app.route("/reference_corpus_select", methods=['POST'])
def corpus_select():
    global corpus
    global reference_corpus
    global conc

    corpora = list_corpora(save_path)
    corpus_filenames = corpora.get_column('corpus').to_list()
    corpus_names = corpora.get_column('name').to_list()
    if request.url_rule.rule == '/corpus_select':
        if 'selected_corpus' in request.form:
            corpus_filename = request.form.get('selected_corpus')
            if corpus_filename and corpus_filename in corpus_filenames:
                corpus = Corpus().load(f'{save_path}{corpus_filename}')
                conc = Conc(corpus)
                conc.set_reference_corpus(reference_corpus) # if new conc created, need to reset reference corpus
    if request.url_rule.rule == '/reference_corpus_select':
        if 'selected_reference_corpus' in request.form:
            reference_corpus_filename = request.form.get('selected_reference_corpus')
            if reference_corpus_filename and reference_corpus_filename in corpus_filenames:
                reference_corpus = Corpus().load(f'{save_path}{reference_corpus_filename}')
                conc.set_reference_corpus(reference_corpus)
    options = []
    for corpus_filename, corpus_name in zip(corpus_filenames, corpus_names):
        if request.url_rule.rule == '/corpus_select' and corpus_name == corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        elif request.url_rule.rule == '/reference_corpus_select' and corpus_name == reference_corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        else:
            options.append(f'<option value="{corpus_filename}">{corpus_name}</option>')
    response = make_response('\n'.join(options))
    response.headers['HX-Trigger'] = 'newCorpus'
    return response