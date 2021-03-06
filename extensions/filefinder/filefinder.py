#!/usr/bin/env python 

import sys, os
from extensions.bas_extension import BaseExtension
from utils import Utils
import subprocess
from config import Config
import datetime

class Filefinder(BaseExtension):
    form_dict = None
    def __init__(self):
        BaseExtension.__init__(self)
        self.utils = Utils()


    def excute(self, form_dict):
        self.form_dict = form_dict
        rTitle = form_dict['rTitle'] 
        rID = form_dict['rID']
        if form_dict.has_key('selection') and form_dict['selection'] != '':
            rTitle = form_dict['selection'].strip()
        html = ''
        localFiles = self.genFileList(self.getMatchFiles(rTitle.strip()).split('\n'))
        if localFiles != '':
            html += '<br>' + localFiles

        alias = ''
        aliasList = []
        record = self.utils.getRecord(rID.strip(), path=form_dict['originFileName'], log=True)
        if record != None and record.get_id().strip() != '':
            ret = self.utils.reflection_call('record', 'WrapRecord', 'get_tag_content', record.line, {'tag' : 'alias'})
            if ret != None:
                alias = ret.strip()
                print 'alias:' + alias
                if alias != '':
                    if alias.find(',') != -1:
                        aliasList = alias.split(',')
                        for als in aliasList:
                            result = self.genFileList(self.getMatchFiles(als.strip()).split('\n'))
                            if result != '':
                                html += als + ':<br>' + result
                    else:
                        aliasList = [alias.strip()]
                        result = self.genFileList(self.getMatchFiles(alias.strip()).split('\n'))
                        if result != '':
                            html += alias + ':<br>' + result

        html += '<div class="ref"><br>search my baidu disk for: <br>' + self.utils.toSmartLink(rTitle, engin="pan.baidu", showText='<font size="2">' + rTitle.replace('%20', ' ') + '</font>', rid=self.form_dict['rID'], library=self.form_dict['originFileName'], module='filefinder') + '<br>'
        count = 1
        for alias in aliasList:
            count += 1
            html += self.utils.toSmartLink(alias.strip(), engin="pan.baidu", showText=str('<font size="2">' + alias + '</font>'), rid=self.form_dict['rID'], library=self.form_dict['originFileName'], module='filefinder') + '<br>'
            #html += '&nbsp;'

        if Config.filefinder_search_db:
            keywords = aliasList + [rTitle.replace('%20', ' ')]
            dbFileList = self.genFileList(self.getMatchFiles2('|'.join(keywords).replace('| ', '|'), [form_dict['originFileName'][form_dict['originFileName'].find('db/') :], form_dict['fileName'][form_dict['fileName'].find('db/') :]]))
            if dbFileList != '':
                html += '<br><br>db files:<br>' + dbFileList

        html += '</div>'

        return html

    def getMatchFiles(self, title):
        output = ''
        for path in Config.filefinder_dirs:
            if path != '':
                cmd = 'find ' + path + ' -iname "*' + title.replace('"', '').replace('%20', ' ').replace(' ', '*') + '*"'
                print 'cmd ' + cmd 
                output += subprocess.check_output(cmd, shell=True)
            if output.find('No such file') != -1:
                continue
            if output.find('//') != -1:
                output = output.replace('//', '/')
        return output

    dbFileArgsDict = {}

    def getMatchFiles2(self, keywords, filterList):
        print filterList
        cmd = 'grep -riE "' + keywords + '" db'
        print cmd
        output = subprocess.check_output(cmd, shell=True)
        fileList = []
        fileCountDict = {}
        self.dbFileArgsDict = {}
        lastFileName = ''
        count = 0
        for line in output.split('\n'):
            fileName = line[0 : line.find(':')].strip()
            igone = False
            for f in filterList:
                if fileName == f.strip():
                    igone = True
                    continue
            if igone:
                continue
            rID = line[line.find(':') + 1 : line.find('|')].strip().replace(' ', '%20') 
            if lastFileName != '' and fileName == lastFileName:
                count += 1
            else:
                count = 1
            if fileName != '':
                fileCountDict[fileName] = count 
                lastFileName = fileName

            if self.dbFileArgsDict.has_key(fileName) == False:
                print fileName
                self.dbFileArgsDict[fileName] = rID
                fileList.append(fileName)
            else:
                if self.dbFileArgsDict[fileName].find(rID) == -1:
                    self.dbFileArgsDict[fileName] = self.dbFileArgsDict[fileName] + '[or]' + rID
        fileCountDict2 = {}
        for k, v in fileCountDict.items():
            if k == '':
                continue
            fileCountDict2[k + '(' + str(v) + ')'] = v
        
        result = []
        for k, v in sorted(fileCountDict2.items(), lambda x, y: cmp(x[1], y[1]), reverse=True) :
            result.append(k)
        return result




    def genFileList(self, dataList):
        if len(dataList) == 0:
            return ''
        print 'genFileList ' + ''.join(dataList)
        html = ''
        count = 0
        if len(dataList) > 0:
            html = '<div class="ref"><ol>'
            for line in dataList:
                if line != '' and (line.find(Config.output_data_to_new_tab_path) == -1 or line.find('.') != -1):
                    count += 1
                    html += '<li><span>' + str(count) + '.</span>'
                    if line.startswith('db/') and (line.endswith(str(datetime.date.today().year)) or line.find('(') != -1):
                        countInfo = ''
                        if line.find('(') != -1:
                            countInfo = '(<font color="red"><b>' + line[line.find('(') + 1 : line.find(')')] + '</b></font>)'
                            line = line[0 : line.find('(')]
                        url = 'http://' + Config.ip_adress + '/?db=' + line[line.find('/') + 1 : line.rfind('/') + 1] + '&key=' + line[line.rfind('/') + 1 :] 
                        if line.find('paper') != -1:
                            url += '&column=1'
                        else:
                            url += '&column=' + Config.column_num + '&width=' + Config.default_width
                        if self.dbFileArgsDict.has_key(line.strip()):
                            url += '&filter=' + self.dbFileArgsDict[line.strip()]
                        html += '<p>' + self.utils.enhancedLink(url, line[line.rfind('/') + 1 :], module='filefinder', rid=self.form_dict['rID'], library=self.form_dict['originFileName'], showText=line[line.rfind('/') + 1 :] + countInfo)
                    else:
                        html += '<p>' + self.utils.enhancedLink(line, line[line.rfind('/') + 1 :], module='filefinder', rid=self.form_dict['rID'], library=self.form_dict['originFileName'])

                    html += '</p></li>'
            html += "</ol></div>"
        if count == 0:
            html = ''

        return html

    def check(self, form_dict):
        return True