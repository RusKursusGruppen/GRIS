
def calendar(id, dFormat = 'yyyyMMdd', selector = 'arrow', time = False, tFormat = 24, seconds = False, futurepast = ''):
    html = '<img src="/static/images/cal.gif" onclick="javascript:NewCssCal(\'{0}\',\'{1}\',\'{2}\',{3},{4},{5},\'{6}\')" class="calendar" />'.format(
        id, dFormat, selector, str(time).lower(), str(tFormat), str(seconds).lower(), futurepast)
    return html
