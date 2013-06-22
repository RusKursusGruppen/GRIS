# -*- coding: utf-8 -*-

from jinja import Markup

def calendar(id, d_Format = 'yyyyMMdd', selector = 'arrow', time = False, t_Format = 24, seconds = False, futurepast = ''):
    html = '<img src="/static/images/cal.gif" onclick="javascript:NewCssCal(\'{0}\',\'{1}\',\'{2}\',{3},{4},{5},\'{6}\')" class="calendar" />'.format(
        id, d_Format, selector, str(time).lower(), str(t_Format), str(seconds).lower(), futurepast)
    return html

def back():
    """Back is a little wonky when there are flashed messages."""
    return Markup("<script>history.back()</script>You have been sent back from where you came")


class WebBuilder(object):
    def __init__(self):
        self.__data__ = []

    def __lshift__(self, args):
        sql = args[0]
        args = args[1:]


    def _newobj(self, obj):
        if not hasattr(obj, "modifier"):
            obj.modifier = False
        if not hasattr(obj, "description"):
            obj.description = ""
        self.__data__.append(obj)

    def create(self, kv=None):
        data = self.__data__
        dbqs = [d.dbq for d in data if hasattr(d, "dbq")]

        mstack = []
        result = ""
        for w in data:

            if w == "CLOSE":
                m = mstack.pop(0)
                result += m.close()
                continue


            if hasattr(w, "dbq"):
                if kv == None:
                    dbqv = None
                else :
                    dbqv = kv[w.dbq]
                temp = w.compile(dbqv)
            else:
                temp = w.compile()
            result += reduce((lambda s, f: f.modify(w, s)), mstack, temp)

            if w.modifier:
                mstack.insert(0,w)

            result += "\n"

        for m in mstack:
            result += m.close()
            result += "\n"

        return result

    def close(self):
        self.__data__.append("CLOSE")

    def form(self):
        self._newobj(_Form())

    def formtable(self):
        self._newobj(_FormTable())

    def waaah(self):
        self._newobj(_Waaah())

    def textfield(self, dbq="", description="", **kwargs):
        self._newobj(_Textfield(dbq, description, kwargs))

    def textarea(self, dbq="", description="", **kwargs):
        self._newobj(_Textarea(dbq, description, kwargs))

    def checkbox(self, dbq="", description="", **kwargs):
        self._newobj(_Checkbox(dbq, description, kwargs))

    #passwordfield
    #radio
    #submit

class _Webobject(object):
    def __init__(self, dbq, description, attributes):
        self.description = description
        self.dbq = dbq
        self.attributes = attributes
        self.modifier = False

    def compile(self, dbqv):
        return ""

    def close(self):
        return ""

    def modify(self, w, html):
        return html

    def _attributes_convert(self, dbqv):
        f = lambda x : x if x != "$" else dbqv
        attributes = {"name":self.dbq}
        if dbqv != None:
            attributes["value"] = dbqv
        attributes.update(self.attributes)
        return attributes

    def _attributes_string(self, attributes=None):
        if type(attributes) != dict:
            dbqv = attributes
            attributes = self._attributes_convert(dbqv)
        string = ' '.join('{0}="{1}"'.format(k,v) for k,v in attributes.iteritems())
        return string

class _Textfield(_Webobject):
    def compile(self, dbqv):
        result = "<input type=text "
        result += self._attributes_string(dbqv)
        result += ">"
        return result

class _Textarea(_Webobject):
    def compile(self, dbqv):
        attributes = self._attributes_convert(dbqv)

        value = attributes.pop("value", None)

        result = "<textarea "
        result += self._attributes_string(attributes)
        result += ">"
        if "value" != None:
            result += value
        result += "</textarea>"
        return result

class _Checkbox(_Webobject):
    def compile(self, dbqv):
        attributes = self._attributes_convert(dbqv)

        value = attributes.pop("value", None)

        result = "<input type=checkbox "
        if dbqv:
            result += "checked "
        result += self._attributes_string(attributes)
        result += ">"
        return result

class _Form(_Webobject):
    def __init__(self):
        self.modifier = True
    def compile(self):
        return "<form method=post>"
    def close(self):
        return "</form>"

class _FormTable(_Webobject):
    def __init__(self):
        self.modifier = True
    def modify(self, w, html):
        return u"<tr>\n<td>{0}</td>\n<td>{1}</td>\n</tr>".format(w.description, html)
    def compile(self):
        return '<table class="formTable">'
    def close(self):
        result = """<tr>
<td colspan="2">
<button type="submit">Opret</button>
<button type="submit" name="cancel" value="cancel">Annuller</button>
</td>
</tr>
</table>"""
        return result


class _Waaah(_Webobject):
    def __init__(self):
        self.modifier = True
    def modify(self, w, html):
        return "<WAAAAAAAAAAAAAAAHHHHHHH>{0}</waaah>".format(html)
    def compile(self):
        return "WAAAHHstart"
    def close(self):
        return "waaahend"

# w = WebBuilder()
# w.form()
# w.formtable()
# w.textfield("name", "Fulde navn")
# w.textfield("address", "Adresse")
# w.textfield("zipcode", "Postnummer")
# w.textfield("city", "By")
# w.textfield("phone", "Telefonnummer")
# w.textfield("email", "Email")
# w.textfield("birthday", "Fødselsdag")
# w.checkbox("driverslicence", u"Har du kørekort?")
# w.textfield("diku_age", u"Hvornår startede du på DIKU?")
# w.textfield("earlier_tours", "Tidligere rusture (brug ; mellem de forskellige turnavne)")
# w.textarea("about_me", "Lidt om mig")
# #w.submit()
# # w.concel()

# print w.create({"name":"mig",
#                 "address":"vej",
#                 "zipcode":"1234",
#                 "city":"bybybyby",
#                 "phone":"12345678",
#                 "email":"abc@def.ghi",
#                 "birthday":"1.2.3",
#                 "driverslicence":1,
#                 "diku_age":"x",
#                 "earlier_tours":"a b c",
#                 "about_me":"Jeg er sej"})
