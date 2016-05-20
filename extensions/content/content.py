#!/usr/bin/env python


import sys, os
from extensions.bas_extension import BaseExtension
from utils import Utils
from update.all_subject import default_subject
from record import ContentRecord



class Content(BaseExtension):

    record_content = {}
   

    def __init__(self):
        BaseExtension.__init__(self)
        self.utils = Utils()

    def loadContent(self, filename):
        name = 'db/metadata/' + filename + '-content'
        if os.path.exists(name):
            f = open(name, 'rU')
            all_lines = f.readlines()
            for line in all_lines:
                if line.startswith('#'):
                    continue
                record = ContentRecord(line)
                if record.get_title().strip() == '':
                    continue
                key = record.get_parentid().strip()
                if self.record_content.has_key(key):
                    self.record_content[key].append(record)
                else:
                    self.record_content[key] = [record]

        #for (k, v) in self.record_content.items():
        #    print k

    
    def excute(self, form_dict):
        divID = form_dict['divID'].encode('utf8')
        rID = form_dict['rID'].encode('utf8')
        if len(self.record_content) == 0:
            fileName = form_dict['fileName'].encode('utf8')
            while (fileName.find('/') != -1) :
                fileName = fileName[fileName.find('/') + 1 :].strip()
            self.loadContent(fileName)
        return self.genContentHtml(rID, divID, form_dict['defaultLinks'])


    def genContentHtml(self, key, content_divID, defaultLinks):
        return self.genMetadataHtml(key, content_divID, defaultLinks)

    def genMetadataHtml(self, key, content_divID, defaultLinks):
        html = '<div class="ref"><ol>'
        count = 0
        if self.record_content.has_key(key):
            #print key
            for r in self.record_content[key]:
                count += 1
                format_index = ''
                pRecord = None
                pid = r.get_parentid().strip()
                if self.record_content.has_key(pid) and key.find('-') != -1:
                    pRecord = self.record_content[pid] 
                    format_index = pid[pid.find('-') + 1 :] + '.' + str(count)
                elif r.get_id().find('-') != -1:
                    format_index = r.get_id()[r.get_id().find('-') + 1 : ].strip()

                html += '<li><span>' + format_index + '</span>'
                if len(format_index) > 4:
                    html += '</li><br/><li>'
                if self.record_content.has_key(r.get_id().strip()) or r.get_url().strip() == '':
                    content_divID += '-' + str(count)
                    linkID = 'a-' + content_divID[content_divID.find('-') + 1 :]
                    title = r.get_title().strip().replace(' ', '%20')
                    script = self.utils.genMoreEnginScript(linkID, content_divID, r.get_id().strip(), title, '-')
                    if r.get_url().strip() != '':
                        html += '<p>' + self.genMetadataLink(r.get_title().strip(), r.get_url().strip())
                    else:
                        html += '<p>' + r.get_title().strip()
                    html += self.utils.getDefaultEnginHtml(title, defaultLinks)
                    if script != "":
                        html += self.utils.genMoreEnginHtml(linkID, script.replace("'", '"'), '...', content_divID, '', False);
                    #contentHtml = self.genContentHtml(r.get_id().strip(), content_divID + '-child', defaultLinks, newIndex)
                    #if contentHtml != '':
                    #    html += contentHtml
                        #div_dict[r.get_id().strip()] = contentHtml
                    html += '</p>'
                elif r.get_url().strip() != '':
                    html += '<p>' + self.genMetadataLink(r.get_title().strip(), r.get_url().strip()) + '</p>'
                    #html += '<a target="_blank" href="' + r.get_url().strip() + '"><p>' + r.get_title().strip() + '</p></a>'

                html += '</li>'
        else:
            return ''

        html += "</ol></div>"
        return html

    def genMetadataLink(self, title, url):
        if url.find('[') != -1:
            ft = url.replace('[', '').replace(']', '').strip()
            r = self.utils.getRecord(ft, '','', False, False)
            key = r.get_path()[r.get_path().find(default_subject) + len(default_subject) + 1 :]
            url = 'http://localhost:5000?db=' + default_subject + '/&key=' + key + '&filter=' + ft  + '&desc=true'

        return self.genMetadataLinkEx(title, url)


    def genMetadataLinkEx(self, title, url):
        if title.find('<a>') != -1:
            title = title.replace('<a>', '<a target="_blank" href="' + url + '">')
        else:
            title = '<a target="_blank" href="' + url + '">' + title + '</a>'
        return title
