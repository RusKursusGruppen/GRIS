
from jinja import Markup

def calendar(id, dFormat = 'yyyyMMdd', selector = 'arrow', time = False, tFormat = 24, seconds = False, futurepast = ''):
    html = '<img src="/static/images/cal.gif" onclick="javascript:NewCssCal(\'{0}\',\'{1}\',\'{2}\',{3},{4},{5},\'{6}\')" class="calendar" />'.format(
        id, dFormat, selector, str(time).lower(), str(tFormat), str(seconds).lower(), futurepast)
    return html

def back():
    """Back is a little wonky when there are flashed messages."""
    return Markup("<script>history.back()</script>You have been sent back from where you came")
