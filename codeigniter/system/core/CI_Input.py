#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys,cgi
PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
    from urllib import quote,unquote
else:
    import urllib.parse



class CI_Input(object):

    def __init__(self,**kwargs):
        self.app=kwargs['app']



    def readfile(self,environ):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        data={}
        if hasattr(form,'list') and len(form.list)>0:
            for elem in form.list:
                if hasattr(elem,'file') and elem.file!=None:
                    try:
                        data[elem.name]=elem.file
                    except Exception as e:
                        pass
                elif elem.file==None or str(elem.type).lower().strip() in ['text/plain'] or (not 'filename' in elem.disposition_options):
                    data[elem.name]=elem.value
                else:
                    data[elem.name]=elem
        return data




    def parse(self,env):
        env['__FORM__DATA__']={}
        data={}
        if 'REQUEST_METHOD' in env.keys() and env['REQUEST_METHOD']=='POST':
            try:
                request_body_size = int(env.get('CONTENT_LENGTH', 0))
                # request_body = env['wsgi.input'].read(request_body_size)
                # d = parse_qs(request_body)
                d = self.readfile(env)
                env['__FORM__DATA__']=d
            except (ValueError):
                request_body_size = 0
        query=env['QUERY_STRING']
        path=env['PATH_INFO']
        paths=path[1:].split(r'/')
        if len(paths)>=2:
            func= paths[ len(paths)-1]
            ctrl= paths[ len(paths)-2]
        elif len(paths)==1:
            ctrl='Index'
            func=paths[0]
        else:
            ctrl='Index'
            func='index'
        items=query.split(r'&')
        for i in items:
            try:
                item=i.split(r'=')
                if len(item)==2:
                    # data[item[0]]=unicode( unquote( item[1]),'utf-8').encode("utf-8")
                    data[item[0]]=unquote( item[1])
                elif len(item)==1 and item[0]!='':
                    data[item[0]]=''
            except Exception as e:
                self.app.logger.warn(e)

       # print(type(env['__FORM__DATA__']))
        data=dict( data.items()+env['__FORM__DATA__'].items())



        #print(data)


        try:
            for k in data.keys():
                if k.find('[]')!=-1:
                    if isinstance(data[k],list):
                        data[k]= eval(data[k][0])
                elif isinstance(data[k],list):
                    data[k]=unicode( data[k][0],'utf-8').encode("utf-8")
        except UnicodeDecodeError as e:
            self.app.logger.warn(str(e)+str(data))
            return data
        except Exception as e:
            self.app.logger.error(e)
        data['__ctrl_name__']=ctrl
        data['__func_name__']=func
        return data