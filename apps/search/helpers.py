import urllib

from django.conf import settings
from django.core.urlresolvers import reverse

import jinja2

from jingo import register, env
from didyoumean import DidYouMean


@register.function
def spellcheck(string, locale='en-US'):
    d = DidYouMean(locale, dict_dir=settings.DICT_DIR)
    return not d.check(string)


@register.filter
@jinja2.contextfilter
def suggestions(context, string, locale='en-US'):
    d = DidYouMean(locale, dict_dir=settings.DICT_DIR)
    words = [(jinja2.escape(w.new), w.corrected) for w in d.suggest(string)]

    newwords = []
    newquery = []
    for w in words:
        newquery.append(w[0])
        if w[1]:
            newwords.append(u'<strong>%s</strong>' % w[0])
        else:
            newwords.append(w[0])

    markup = '<a href="{url}">{text}</a>'

    q = u' '.join(newquery)
    text = u' '.join(newwords)
    query_dict = context['request'].GET.copy()
    query_dict['q'] = q
    if 'page' in query_dict:
        query_dict['page'] = 1

    query_string = urllib.urlencode(query_dict.items())

    url = u'%s?%s' % (reverse('search'), query_string)

    return jinja2.Markup(markup.format(url=jinja2.escape(url), text=text))