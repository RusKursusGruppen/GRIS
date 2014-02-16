# -*- coding: utf-8 -*-

#import re
import markdown as md

from jinja2 import evalcontextfilter, Markup, escape

# _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

#app = Flask(__name__)

# #@app.template_filter()
# @evalcontextfilter
# def nl2br(eval_ctx, value):
#     result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
#         for p in _paragraph_re.split(escape(value)))
#     if eval_ctx.autoescape:
#         result = Markup(result)
#     return result

def nl2br(text):
    result = str(text).replace("\n", "<br/>")
    return Markup(result)

def markdown(text):
    result = md.markdown(escape(text))
    return Markup(result)


def money(amount):
    amount = str(amount)
    if amount == "":
        return ""
    first = amount[:-2]
    second = amount[-2:]
    # if second == '00':
    #     return "{0},-".format(first)
    # else:
    return "{0}.{1},-".format(first, second)
