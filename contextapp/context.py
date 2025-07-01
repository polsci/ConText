from conc.corpus import Corpus
from conc.conc import Conc
from conc.corpora import list_corpora
from conc.core import set_logger_state
from flask import Flask, render_template, redirect, url_for, request, make_response
from flask_wtf.csrf import CSRFProtect
from flaskwebgui import FlaskUI 
import polars as pl
import secrets
import os
import nh3
import argparse

app = Flask(__name__)

secret_file = os.path.expanduser('./.context')
if not os.path.exists(secret_file):
    with open(secret_file, 'w') as f:
        f.write(secrets.token_hex(32))
with open(secret_file) as f:
    app.config['SECRET_KEY'] = f.read().strip()

csrf = CSRFProtect(app)

global corpora_path
global corpus
global reference_corpus
global conc
global page_size

corpus = None
reference_corpus = None
conc = None
current_corpus_path = None
current_reference_corpus_path = None
current_order = '1R2R3R'
page_size = 20

def clean(user_input):
    return nh3.clean(user_input)

def _get_nav(context_type, pane = 'context-right', reports = [], page = None, max_page = None):
    current_path = request.path
    paging_buttons = ''
    if page is not None and max_page is not None and max_page > 1:
        page = int(page)
        if page > 1:
            url_without_page = current_path.split('/')[:-1]
            previous_page = '/'.join(url_without_page + [str(page-1)])
            start_page = '/'.join(url_without_page + ['1'])
            paging_buttons += f'<button class="context-button context-start-button" hx-get="{start_page}" hx-target="#{pane}"><span>First Page</span></button>'
            paging_buttons += f'<button class="context-button context-previous-button" hx-get="{previous_page}" hx-target="#{pane}"><span>Previous Page</span></button>'
        else:
            paging_buttons += '<button class="context-button context-start-button disabled" disabled><span>First Page</span></button>'
            paging_buttons += '<button class="context-button context-previous-button disabled" disabled><span>Previous Page</span></button>'
        if page < max_page:
            url_without_page = current_path.split('/')[:-1]
            next_page = '/'.join(url_without_page + [str(page+1)])
            end_page = '/'.join(url_without_page + [str(max_page)])
            paging_buttons += f'<button class="context-button context-next-button" hx-get="{next_page}" hx-target="#{pane}"><span>Next Page</span></button>'
            paging_buttons += f'<button class="context-button context-end-button" hx-get="{end_page}" hx-target="#{pane}"><span>Last Page</span></button>'
        else:
            paging_buttons += '<button class="context-button context-next-button disabled" disabled><span>Next Page</span></button>'
            paging_buttons += '<button class="context-button context-end-button disabled" disabled><span>Last Page</span></button>'

    
    if len(reports) > 0:
        reports_button = '<button class="context-button context-reports-button"><span>Reports</span></button>' #on mouseover show .reports-nav end on mouseout hide .reports-nav end
        reports_nav = '<ul class="reports-nav">'
        reports_nav += f'<li>Current View: {context_type.title()}</li>'
        if type(reports) is list:
            reports = {report:None for report in reports}
        for report in reports:
            report_title = report.title()
            if reports[report] is None:
                reports[report] = current_path.replace(context_type, report.replace(' ', '').lower())
            reports_nav += f'<li>Switch to <span class="context-clickable" hx-target="#{pane}" hx-get="{reports[report]}">{report_title}</a></li>'
        reports_nav += '</ul>'
    else:
        reports_nav = ''
        reports_button = ''
        
    return f'<nav id="{pane}-nav" class="context-nav">{paging_buttons}{reports_button}{reports_nav}<button class="context-button context-options-button" _="on click toggle .show-form on #context-settings-form" hx-get="/{context_type}-settings" hx-target="#context-settings-form"><span>Options</span></button></nav>'

def _get_max_page(result):
    paging_descriptor = [line for line in result.formatted_data if line.startswith('Page ')]
    if len(paging_descriptor) == 0:
        return 1
    else:
        return int(paging_descriptor[0].split(' ')[-1])

def _get_default():
    corpus_info = render_template("corpus-info.html", title = 'Corpus Information', table = corpus.report().to_html(), reference_corpus_title = 'Reference Corpus', reference_corpus_table = reference_corpus.report().to_html())
    return render_template("context-default.html", corpus_slug = corpus.slug, reference_corpus_slug = reference_corpus.slug, corpus_info = corpus_info)

def _get_query(search, order):
    return render_template("context-query.html", search_url = url_for('form_search', search = search), concordance_url = url_for('concordance', search=search, order=order, page = 1), clusters_url = url_for('clusters', search=search, order=order, page = 1))

@app.route("/")
def home():
    search = ''
    order = '1R2R3R'
    if corpus is None or reference_corpus is None:
        return render_template("index.html", search = search, order=order, context=render_template("context-nocorpus.html"))
    else:
        context = _get_default()
    return render_template("index.html", search = search, order=order, context=context)

@app.route("/default-home", methods=['POST'])
def default_home():
    context = _get_default()
    response_url = url_for('home')
    response = make_response(context)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    return response

@app.route('/screen/<size>', methods=['POST'])
def small_screen(size):
    global page_size
    if size == 'small':
        page_size = 10
    else:
        page_size = 20
    return ''


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
    return redirect(url_for('keywords', corpus_slug=corpus.slug, reference_corpus_slug=reference_corpus.slug, page = 1))

@app.route('/keywords/<corpus_slug>/<reference_corpus_slug>/<page>')
def keywords(corpus_slug, reference_corpus_slug, page = 1):
    corpus_slug = clean(corpus_slug) # not used, but keeping consistent
    reference_corpus_slug = clean(reference_corpus_slug) # not used anyway, but keeping consistent
    page = clean(page)
    result = conc.keywords(min_document_frequency = 5, min_document_frequency_reference = 5, show_document_frequency = True, page_current = int(page), page_size = page_size)
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), result.df.select(pl.col('token')).to_series(), pl.lit('/'), pl.lit(current_order), pl.lit('">'), result.df.select(pl.col('token')).to_series(), pl.lit('</span>')).alias('token'),
    )
    nav = _get_nav('keywords', pane = 'context-right', reports = ['frequencies'], page = page, max_page = _get_max_page(result))
    title = '<h2>Keywords</h2>'
    return nav + title + result.to_html()

@app.route('/frequencies/<corpus_slug>/<reference_corpus_slug>/<page>')
def frequencies(corpus_slug, reference_corpus_slug, page = 1):
    corpus_slug = clean(corpus_slug) # not used, but keeping consistent
    reference_corpus_slug = clean(reference_corpus_slug) # not used anyway, but keeping consistent
    page = clean(page)
    result = conc.frequencies(show_document_frequency = True, page_current = int(page), page_size = page_size)
    result.df = result.df.collect()
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), result.df.select(pl.col('token')).to_series(), pl.lit('/'), pl.lit(current_order), pl.lit('">'), result.df.select(pl.col('token')).to_series(), pl.lit('</span>')).alias('token'),
    )
    nav = _get_nav('frequencies', pane = 'context-right', reports = ['keywords'], page = page, max_page = _get_max_page(result))
    title = '<h2>Frequencies</h2>'
    return nav + title + result.to_html()

@app.route('/text-from-concordanceplot/<search>/<order>', methods=['POST'])
def text_from_concordanceplot(search, order):
    search = clean(search)
    order = clean(order)
    doc = int(clean(request.form.get('doc')))
    offset = int(clean(request.form.get('offset')))
    token_sequence, index_id = corpus.tokenize(search, simple_indexing=True)
    sequence_len = len(token_sequence[0])
    start_index = corpus.text(doc).doc_position_to_corpus_position(offset)
    return redirect(url_for('text', search=search, order=order, doc_id=doc, start_index=start_index, end_index=start_index + sequence_len - 1))

@app.route('/text/<search>/<order>/<doc_id>/<start_index>/<end_index>')
def text(search, order, doc_id, start_index, end_index):
    search = clean(search)
    order = clean(order)
    doc_id = clean(doc_id)
    start_index = clean(start_index)
    end_index = clean(end_index)
    doc = corpus.text(int(doc_id))
    result = doc.as_string(highlighted_token_range = (int(start_index), int(end_index)))
    metadata = doc.get_metadata().to_html()
    nav = _get_nav('text', pane = 'context-left', reports = {'clusters': url_for('clusters', search = search, order = order, page = 1), 'collocates': url_for('collocates', search = search, order = order, page = 1)})
    return render_template("text.html", title = 'Text', result = result, metadata = metadata, nav = nav)

@app.route('/collocates/<search>/<order>/<page>')
def collocates(search, order, page = 1):
    search = clean(search)
    order = clean(order)
    page = clean(page)
    result = conc.collocates(search, page_current = int(page), page_size = page_size)
    nav = _get_nav('collocates', pane = 'context-left', reports = ['clusters'], page = page, max_page = _get_max_page(result))
    title = '<h2>Collocates</h2>'
    return nav + title +  result.to_html()

@app.route('/clusters/<search>/<order>/<page>')
def clusters(search, order, page = 1):
    search = clean(search)
    order = clean(order)
    page = clean(page)
    if 'R' not in order:
        ngram_token_position = 'RIGHT'
    elif 'L' not in order:
        ngram_token_position = 'LEFT'
    else:
        ngram_token_position = 'MIDDLE'
    result = conc.ngrams(search, ngram_length = None, ngram_token_position = ngram_token_position, page_current = int(page), page_size = page_size)
    if result.df.is_empty():
        return f'&nbsp;'
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-main" hx-get="/query-context/'), result.df.select(pl.col('ngram')).to_series(), pl.lit('/'), pl.lit(order), pl.lit('">'), result.df.select(pl.col('ngram')).to_series(), pl.lit('</span>')).alias('ngram'),
    )
    nav = _get_nav('clusters', pane = 'context-left', reports = ['collocates'], page = page, max_page = _get_max_page(result))
    title = '<h2>Clusters</h2>'
    return nav + title + result.to_html() 

@app.route('/concordance/<search>/<order>/<page>')
def concordance(search, order, page = 1):
    search = clean(search)
    order = clean(order)
    page = clean(page)
    token_sequence, index_id = corpus.tokenize(search, simple_indexing=True)
    sequence_len = len(token_sequence[0])
    result = conc.concordance(search, context_length = 20, order = order, show_all_columns = True, page_current = int(page), ignore_punctuation=True, page_size = page_size)
    if result.df.is_empty():
        return f'<h2>0 results for &quot;{search}&quot;</h2>'
    result.df = result.df.with_columns(
        pl.concat_str(pl.lit('<span class="context-clickable" hx-target="#context-left" hx-get="/text/'), pl.lit(search), pl.lit('/'), pl.lit(order), pl.lit('/'), result.df.select(pl.col('doc_id')).to_series(), pl.lit('/'), result.df.select(pl.col('index')).to_series(), pl.lit('/'), result.df.select(pl.col('index')).to_series() + pl.lit(sequence_len-1), pl.lit('">'), result.df.select(pl.col('node')).to_series(), pl.lit('</span>')).alias('node'),
    )
    result.df = result.df[['doc_id', 'left', 'node', 'right']]
    nav = _get_nav('concordance', pane = 'context-right', reports = ['concordance plot'], page = page, max_page = _get_max_page(result))
    title = '<h2>Concordance</h2>'
    return nav + title + result.to_html()

@app.route("/concordanceplot/<search>/<order>/<page>")
def concordanceplot(search, order, page = 1):
    search = clean(search)
    order = clean(order)
    page = clean(page)
    nav = _get_nav('concordanceplot', pane = 'context-right', reports = ['concordance'], page = 1, max_page = None)
    title = '<h2>Concordance Plot</h2>'
    context = conc.concordance_plot(search).to_html()
    return render_template("context-concordanceplot.html", nav = nav, title = title, context = context)

@app.route("/query/<search>/<order>")
def query(search, order):
    if corpus is None or reference_corpus is None:
        return redirect(url_for('home'))
    global current_order
    search = clean(search)
    order = clean(order)
    current_order = order
    context_html = _get_query(search, order)
    return render_template("index.html", search = search, order=order, context=context_html)

@app.route("/form-search/<search>", methods=['GET'])
def form_search(search):
    search = clean(search)
    return render_template("form-search.html", search=search)

@app.route("/query-context", methods=['POST'])
def query_context_redirect(): 
    search = clean(request.form.get('search'))
    order = clean(request.form.get('order'))
    if not search:
        return redirect(url_for('default_home'))
    else:
        return redirect(url_for('query_context', search=search, order=order))

@app.route("/query-context/<search>/<order>", methods=['GET'])
def query_context(search, order): 
    global current_order
    search = clean(search)
    order = clean(order)
    current_order = order
    search = search.strip()
    context = _get_query(search, order)
    response = make_response(context)
    response_url = url_for('query', search=search, order=order)
    response.headers['HX-Replace-Url'] = response_url
    response.headers['HX-Push-Url'] = response_url
    response.headers['HX-Trigger'] = 'newContext' 
    return response

@app.route("/detail", methods=['POST'])
def detail_redirect():
    global corpus
    return redirect(url_for('detail', corpus_slug=corpus.slug))

@app.route("/detail/<corpus_slug>", methods=['GET'])
def detail(corpus_slug):
    corpus_slug = clean(corpus_slug) # not used, but keeping consistent
    corpus_info = f"Word tokens: {corpus.word_token_count/1_000_000:.2f} million &bull; Documents: {corpus.document_count:,}"
    return render_template("detail.html", 
                           corpus_name=corpus.name, 
                           corpus_info=corpus_info)

@app.route("/new-corpus", methods=['POST'])
def new_corpus():
    if corpus is None: 
        return ''
    else:
        context = ''
        response = make_response(context)
        response.headers['HX-Trigger'] = 'newCorpus'
        return response

@app.route("/frequencies-settings", methods=['GET'])
@app.route("/keywords-settings", methods=['GET'])
@app.route("/concordance-settings", methods=['GET'])
@app.route("/concordanceplot-settings", methods=['GET'])
@app.route("/collocates-settings", methods=['GET'])
@app.route("/clusters-settings", methods=['GET'])
@app.route("/text-settings", methods=['GET'])
def report_settings():
    title = request.path.replace('/', '').replace('-', ' ').title()
    if 'Concordanceplot' in title:
        title = 'Concordance Plot Settings'
    return render_template("report-settings.html", title = title)

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

    corpora = list_corpora(corpora_path)
    corpus_filenames = corpora.get_column('corpus').to_list()
    corpus_names = corpora.get_column('name').to_list()
    trigger_new_corpus = False
    if request.url_rule.rule == '/corpus-select':
        if 'selected_corpus' in request.form:
            corpus_filename = clean(request.form.get('selected_corpus'))
            if corpus_filename and corpus_filename in corpus_filenames and corpus_filename != current_corpus_path:
                corpus = Corpus().load(f'{corpora_path}{corpus_filename}')
                conc = Conc(corpus)
                if conc is not None and reference_corpus is not None:
                    conc.set_reference_corpus(reference_corpus) # if new conc created, need to reset reference corpus
                current_corpus_path = corpus.corpus_path
                trigger_new_corpus = True
    if request.url_rule.rule == '/reference-corpus-select':
        if 'selected_reference_corpus' in request.form:
            reference_corpus_filename = clean(request.form.get('selected_reference_corpus'))
            if reference_corpus_filename and reference_corpus_filename in corpus_filenames and reference_corpus_filename != current_reference_corpus_path:
                reference_corpus = Corpus().load(f'{corpora_path}{reference_corpus_filename}')
                if conc is not None:
                    conc.set_reference_corpus(reference_corpus)
                current_reference_corpus_path = reference_corpus.corpus_path
                trigger_new_corpus = True
    options = []
    options.append('<option value=""> - </option>')
    for corpus_filename, corpus_name in zip(corpus_filenames, corpus_names):
        if request.url_rule.rule == '/corpus-select' and corpus is not None and corpus_name == corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        elif request.url_rule.rule == '/reference-corpus-select' and reference_corpus is not None and corpus_name == reference_corpus.name:
            options.append(f'<option value="{corpus_filename}" selected>{corpus_name}</option>')
        else:
            options.append(f'<option value="{corpus_filename}">{corpus_name}</option>')
    response = make_response('\n'.join(options))
    if trigger_new_corpus:
        response.headers['HX-Trigger'] = 'newCorpus'
    return response

def main():
    global corpora_path

    parser = argparse.ArgumentParser(description='Run ConText.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on (ignored in production mode, defaults to 5000 in development mode)')
    parser.add_argument('--corpora', type=str, default='./', help='Path to find corpora')
    parser.add_argument('--mode', type=str, default='production', help='Mode to run the server (production or development)')
    args = parser.parse_args()

    corpora_path = args.corpora
    if not os.path.exists(corpora_path):
        print(f"Corpora path '{corpora_path}' does not exist. Please provide a valid path.")
        exit(1)

    if args.mode == 'development':
        print(f"Starting server on port {args.port}")
        print(f"Load a browser at http://127.0.0.1:{args.port}/")
        app.run(debug=True, use_reloader=True, port=args.port)
    else:
        FlaskUI(app=app, server="flask", fullscreen=True).run()

if __name__ == '__main__':
    main()
