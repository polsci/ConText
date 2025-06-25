from conc.corpus import Corpus
from conc.conc import Conc
from conc.corpora import list_corpora
from conc.core import set_logger_state
from flask import Flask, render_template, redirect, url_for, request, make_response
import polars as pl

# conc result - implement summary value so can pass to context
# document.documentElement.scrollTop = document.getElementById("selected").offsetTop-100;

app = Flask(__name__)

save_path = '/home/geoff/data/conc-test-corpora/'

global corpus
global reference_corpus
global conc

corpus = Corpus().load(f'{save_path}reuters.corpus')
reference_corpus = Corpus().load(f'{save_path}brown.corpus')
conc = Conc(corpus)
current_corpus_path = corpus.corpus_path
current_reference_corpus_path = reference_corpus.corpus_path
current_order = '1R2R3R'
conc.set_reference_corpus(reference_corpus)

def _get_nav(context_type, pane = 'context-right', reports = []):
    if len(reports) > 0:
        reports_button = '<button class="context-button context-reports-button"><span>Reports</span></button>' #on mouseover show .reports-nav end on mouseout hide .reports-nav end
        reports_nav = '<ul class="reports-nav">'
        current_path = request.path
        reports_nav += f'<li>Current View: {context_type.title()}</li>'
        for report in reports:
            report_title = report.title()
            if ' ' in report:
                report = report.replace(' ', '').lower()
            reports_nav += f'<li>Switch to <span class="context-clickable" hx-target="#{pane}" hx-get="{current_path.replace(context_type, report)}">{report_title}</a></li>'
        reports_nav += '</ul>'
    else:
        reports_nav = ''
        reports_button = ''
        
    return f'<nav id="{pane}-nav" class="context-nav">{reports_button}{reports_nav}<button class="context-button context-options-button" _="on click toggle .show-form on #context-settings-form" hx-get="/{context_type}-settings" hx-target="#context-settings-form"><span>Options</span></button></nav>'

def _get_default():
    corpus_info = render_template("corpus-info.html", title = 'Corpus Information', table = corpus.report().to_html(), reference_corpus_title = 'Reference Corpus', reference_corpus_table = reference_corpus.report().to_html())
    return render_template("context-default.html", corpus_slug = corpus.slug, reference_corpus_slug = reference_corpus.slug, corpus_info = corpus_info)

def _get_query(search, order):
    return render_template("context-query.html", search_url = url_for('form_search', search = search), concordance_url = url_for('concordance', search=search, order=order), clusters_url = url_for('clusters', search=search, order=order))

# def _get_query_html(search_string, order_string):
#     context_left = '<h2>Clusters</h2>' + conc.ngrams(search_string, ngram_length = None).to_html() 
#     context_right = '<h2>Concordance</h2>'
    
#     context_right += f'<button id="context-chart-button" hx-target="#context-right" hx-post="/concordanceplot/{search_string}/{order_string}"><span>Concordance Plot</span></button>'
#     context_right += conc.concordance(search_string, context_length = 20, order = order_string).to_html()
#     context_full = ''
#     return render_template("context.html", 
#                                context_left=context_left, 
#                                context_right=context_right, 
#                                context_full=context_full,
#                                context_data_title=f'ConText : {search_string} ({order_string})'
#                                )


@app.route("/")
def home():
    search_string = ''
    order_string = '1R2R3R'
    context = _get_default()
    return render_template("index.html", search = search_string, order=order_string, context=context)

@app.route("/default-home", methods=['POST'])
def default_home():
    context = _get_default()
    response_url = url_for('home')
    response = make_response(context)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    return response

@app.route('/corpus-info', methods=['POST'])
def corpus_info_redirect():
    global corpus
    return redirect(url_for('corpus_info', corpus_slug=corpus.slug, reference_corpus_slug=reference_corpus.slug))

@app.route('/corpus-info/<corpus_slug>/<reference_corpus_slug>')
def corpus_info(corpus_slug, reference_corpus_slug):
    return render_template("corpus-info.html", title = 'Corpus Information', table = corpus.report().to_html(), reference_corpus_title = 'Reference Corpus', reference_corpus_table = reference_corpus.report().to_html())

@app.route('/keywords', methods=['POST'])
def keywords_redirect():
    global corpus
    return redirect(url_for('keywords', corpus_slug=corpus.slug, reference_corpus_slug=reference_corpus.slug))

@app.route('/keywords/<corpus_slug>/<reference_corpus_slug>')
def keywords(corpus_slug, reference_corpus_slug):
    result = conc.keywords(min_document_frequency_reference = 5, show_document_frequency = True)
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), result.df.select(pl.col('token')).to_series(), pl.lit('/'), pl.lit(current_order), pl.lit('">'), result.df.select(pl.col('token')).to_series(), pl.lit('</span>')).alias('token'),
    )
    nav = _get_nav('keywords', pane = 'context-right', reports = ['frequencies'])
    title = '<h2>Keywords</h2>'
    return nav + title + result.to_html()

@app.route('/frequencies/<corpus_slug>/<reference_corpus_slug>')
def frequencies(corpus_slug, reference_corpus_slug):
    result = conc.frequencies(show_document_frequency = True)
    result.df = result.df.collect()
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), result.df.select(pl.col('token')).to_series(), pl.lit('/'), pl.lit(current_order), pl.lit('">'), result.df.select(pl.col('token')).to_series(), pl.lit('</span>')).alias('token'),
    )
    nav = _get_nav('keywords', pane = 'context-right', reports = ['keywords'])
    title = '<h2>Frequencies</h2>'
    return nav + title + result.to_html()

@app.route('/text/<doc_id>/<start_index>/<end_index>')
def text(doc_id, start_index, end_index):
    doc = corpus.text(int(doc_id))
    result = doc.as_string(highlighted_token_range = (int(start_index), int(end_index)))
    metadata = doc.get_metadata().to_html()
    nav = _get_nav('text', pane = 'context-left', reports = ['clusters', 'collocates'])
    return render_template("text.html", title = 'Text', result = result, metadata = metadata, nav = nav)

@app.route('/collocates/<search>/<order>')
def collocates(search, order):
    nav = _get_nav('collocates', pane = 'context-left', reports = ['clusters'])
    title = '<h2>Collocates</h2>'
    return nav + title + conc.collocates(search).to_html() 

@app.route('/clusters/<search>/<order>')
def clusters(search, order):
    clusters_result = conc.ngrams(search, ngram_length = None)
    clusters_result.df = clusters_result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), clusters_result.df.select(pl.col('ngram')).to_series(), pl.lit('/'), pl.lit(order), pl.lit('">'), clusters_result.df.select(pl.col('ngram')).to_series(), pl.lit('</span>')).alias('ngram'),
    )
    nav = _get_nav('clusters', pane = 'context-left', reports = ['collocates'])
    title = '<h2>Clusters</h2>'
    return nav + title + clusters_result.to_html() 

@app.route('/concordance/<search>/<order>')
def concordance(search, order):
    token_sequence, index_id = corpus.tokenize(search, simple_indexing=True)
    sequence_len = len(token_sequence[0])
    result = conc.concordance(search, context_length = 20, order = order, show_all_columns = True)
    if result.df.is_empty():
        return f'<h2>No concordance results {search}</h2>'
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-left" hx-get="/text/'), result.df.select(pl.col('doc_id')).to_series(), pl.lit('/'), result.df.select(pl.col('index')).to_series(), pl.lit('/'), result.df.select(pl.col('index')).to_series() + pl.lit(sequence_len-1), pl.lit('">'), result.df.select(pl.col('node')).to_series(), pl.lit('</span>')).alias('node'),
    )
    result.df = result.df[['doc_id', 'left', 'node', 'right']]
    nav = _get_nav('concordance', pane = 'context-right', reports = ['concordance plot'])
    title = '<h2>Concordance</h2>'
    return nav + title + result.to_html()

@app.route("/concordanceplot/<search>/<order>")
def concordanceplot(search, order):
    # TODO escape search and order
    nav = _get_nav('concordanceplot', pane = 'context-right', reports = ['concordance'])
    title = '<h2>Concordance Plot</h2>'
    context = conc.concordance_plot(search).to_html()
    return nav + title + context

@app.route("/query/<search>/<order>")
def query(search, order):
    # TODO escape search and order
    global current_order
    current_order = order
    context_html = _get_query(search, order)
    return render_template("index.html", search = search, order=order, context=context_html)

@app.route("/form-search/<search>", methods=['GET'])
def form_search(search):
    return render_template("form-search.html", search=search)

@app.route("/query-context", methods=['POST'])
def query_context_redirect(): # TODO escape search and order
    search = request.form.get('search')
    order = request.form.get('order')
    if not search:
        return redirect(url_for('default_home'))
    else:
        return redirect(url_for('query_context', search=search, order=order))

@app.route("/query-context/<search>/<order>", methods=['GET'])
def query_context(search, order): # TODO escape search and order
    global current_order
    current_order = order
    search = search.strip()
    context = _get_query(search, order)
    response = make_response(context)
    response_url = url_for('query', search=search, order=order)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    response.headers['HX-Trigger'] = 'newContext' #  hx-trigger="newContext from:body" hx-swap="outerHTML" hx-get="{{ search_url }}" hx-target="#form-search"
    return response

@app.route("/detail", methods=['POST'])
def detail_redirect():
    global corpus
    return redirect(url_for('detail', corpus_slug=corpus.slug))

@app.route("/detail/<corpus_slug>", methods=['GET'])
def detail(corpus_slug):
    #corpus_info = f"{corpus.word_token_count:,} word tokens ({corpus.word_token_count/1_000_000:.2f} million tokens), {corpus.document_count:,} documents loaded"
    corpus_info = f"Word tokens: {corpus.word_token_count/1_000_000:.2f} million &bull; Documents: {corpus.document_count:,}"
    return render_template("detail.html", 
                           corpus_name=corpus.name, 
                           corpus_info=corpus_info)

@app.route("/new-corpus", methods=['POST'])
def new_corpus():
    context = ''
    response = make_response(context)
    response.headers['HX-Trigger'] = 'newCorpus'
    return response

@app.route("/settings", methods=['GET'])
def settings():
    return render_template("settings.html")

@app.route("/corpus-select", methods=['POST'])
@app.route("/reference-corpus-select", methods=['POST'])
def corpus_select():
    global corpus
    global reference_corpus
    global conc
    global current_corpus_path
    global current_reference_corpus_path

    corpora = list_corpora(save_path)
    corpus_filenames = corpora.get_column('corpus').to_list()
    corpus_names = corpora.get_column('name').to_list()
    trigger_new_corpus = False
    if request.url_rule.rule == '/corpus-select':
        if 'selected_corpus' in request.form:
            corpus_filename = request.form.get('selected_corpus')
            if corpus_filename and corpus_filename in corpus_filenames and corpus_filename != current_corpus_path:
                corpus = Corpus().load(f'{save_path}{corpus_filename}')
                conc = Conc(corpus)
                conc.set_reference_corpus(reference_corpus) # if new conc created, need to reset reference corpus
                current_corpus_path = corpus.corpus_path
                trigger_new_corpus = True
    if request.url_rule.rule == '/reference-corpus-select':
        if 'selected_reference_corpus' in request.form:
            reference_corpus_filename = request.form.get('selected_reference_corpus')
            if reference_corpus_filename and reference_corpus_filename in corpus_filenames and reference_corpus_filename != current_reference_corpus_path:
                reference_corpus = Corpus().load(f'{save_path}{reference_corpus_filename}')
                conc.set_reference_corpus(reference_corpus)
                current_reference_corpus_path = reference_corpus.corpus_path
                trigger_new_corpus = True
    options = []
    for corpus_filename, corpus_name in zip(corpus_filenames, corpus_names):
        if request.url_rule.rule == '/corpus-select' and corpus_name == corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        elif request.url_rule.rule == '/reference-corpus-select' and corpus_name == reference_corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        else:
            options.append(f'<option value="{corpus_filename}">{corpus_name}</option>')
    response = make_response('\n'.join(options))
    if trigger_new_corpus:
        response.headers['HX-Trigger'] = 'newCorpus'
    return response