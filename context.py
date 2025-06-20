from conc.corpus import Corpus
from conc.conc import Conc
from conc.corpora import list_corpora
from conc.core import set_logger_state
from conc.result import Result
from flask import Flask, render_template, redirect, url_for, request, make_response

# TODO:
# show settings on load
# paging
# links to context
# formatting of tables 
# handle escaping
# set / load corpus and reference corpus
# probably update conc to use Result object for corpus info etc
# make corpus name at top a link to the default view
# set defaults for various reports
# low priority - update title on url changes
# low priority - do loading thing - hx-indicator

# Conc TODO:
# conc needs to center node in concordance Result
# needs a way to get Corpus summary as a result
# implement summary data for Result - so can render them how i like
# default document id as doc id in concordance results

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
def _get_default_html():
    context_left = '<div class="context-summaries"><h2>Corpus Information</h2>'
    context_left += Result('summary', corpus.info(), 'Corpus Summary', '', {}, []).to_html()
    context_left += '<h2>Reference Corpus Information</h2>'
    context_left += Result('summary', reference_corpus.info(), 'Reference Corpus Summary', '', {}, []).to_html()
    context_left += '</div>'
    context_right = '<h2>Keywords</h2>' + conc.keywords(min_document_frequency_reference = 5, show_document_frequency = True).to_html()
    context_full = ''
    context_data_title = f'ConText'
    return render_template("context.html", 
                               context_left=context_left, 
                               context_right=context_right, 
                               context_full=context_full,
                               context_data_title=context_data_title
                              
                               )

def _get_query_html(search_string, order_string):
    context_left = '<h2>Clusters</h2>' + conc.ngrams(search_string).to_html()
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

def _get_concordanceplot_html(search_string, order_string):
    context = '<h2>Concordance Plot</h2>'
    context += f'<button id="context-table-button"><span>Concordance Plot</span></button>'
    return context


@app.route("/")
def home():
    search_string = ''
    order_string = '1R2R3R'
    context = _get_default_html()
    return render_template("index.html", search = search_string, order=order_string, context=context)

@app.route("/default_home")
def default_home():
    context = _get_default_html()
    response_url = url_for('home')
    response = make_response(context)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    return response

@app.route("/concordanceplot/<search>/<order>", methods=['POST'])
def concordanceplot(search, order):
    # TODO escape search and order
    context = _get_concordanceplot_html(search, order)
    return context

@app.route("/query/<search>/<order>")
def query(search, order):
    # TODO escape search and order
    context_html = _get_query_html(search, order)
    return render_template("index.html", search = search, order=order, context=context_html)

@app.route("/query_context", methods=['POST'])
def query_context():
    search_string = request.form.get('search') # TODO escape search and order
    order_string = request.form.get('order')
    context = _get_query_html(search_string, order_string)
    response = make_response(context)
    response_url = url_for('query', search=search_string, order=order_string)
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
    if request.url_rule.rule == '/reference_corpus_select':
        if 'reference_corpus' in request.form:
            reference_corpus_filename = request.form.get('reference_corpus')
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
    return '\n'.join(options)