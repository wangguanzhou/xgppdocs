from django.shortcuts import render
from settings import BASE_DIR
import os
from ftplib import FTP
import xlrd
from .forms import TDocFilter

SA2Meetings = [
    {'name': 'SA2-126', 'time': 'Feb 2018', 'city': 'Montreal',},
    {'name': 'SA2-125', 'time': 'Jan 2018', 'city': 'Gothenburg',},
]

FTP_3GPP_HOST = 'ftp.3gpp.org'
SA2Path = '/tsg_sa/WG2_Arch/'
MeetingTDocPath = {
    'SA2-126': SA2Path+'TSGS2_126_Montreal/Docs/',
    'SA2-125': SA2Path+'TSGS2_125_Gothenburg/Docs/',
}
TDocListNames = {
    'SA2-126': 'TDoc_List_Meeting_SA2#126.xlsx',
    'SA2-125': 'TDoc_List_Meeting_SA2#125.xlsx',
}

TDOC_ROOT = '/var/www/xgppdocs/tdocs/'

def homepage(request):
    context = {}
    context['sa2meetings'] = SA2Meetings
    return render(request, 'homepage.html', context)

def showtdoclist(request):
    context = {}
    context['sa2meetings'] = SA2Meetings
    if request.GET:
        meeting_no = request.GET['meeting']
        context['meeting_no'] = meeting_no
        if tdoc_list_exist(meeting_no):
            tdoc_list = get_tdoc_list(meeting_no)
            context['tdoc_list'] = tdoc_list
            tdoc_filter = TDocFilter()
            tdoc_filter.fields['tdoc_source'].choices = get_tdoc_source_options(tdoc_list)
            tdoc_filter.fields['tdoc_agendaitem'].choices = get_tdoc_agendaitem_options(tdoc_list)
            context['tdoc_filter'] = tdoc_filter

        return render(request, 'tdoclist.html', context)
        
def tdoc_list_exist(meeting_no):
    tdoclist_path = os.path.join(BASE_DIR + '/tdoclist/')
    tdoclist_file = tdoclist_path + TDocListNames[meeting_no]
    if not os.path.exists(tdoclist_file):
        ftp = FTP(FTP_3GPP_HOST)
        ftp.login()
        ftp.cwd(MeetingTDocPath[meeting_no])
        with open(tdoclist_file, 'wb') as f:
            ftp.retrbinary('RETR '+TDocListNames[meeting_no], f.write)
        ftp.close()
    if os.path.exists(tdoclist_file):
        return True
    else:
        return False

def tdoc_exist(meeting_no, tdoc_number):
    tdoc_file = TDOC_ROOT + meeting_no + '/' + tdoc_number 
    for ext in ['.doc', '.docx', '.pdf', '.ppt']:
        if os.path.exists(tdoc_file + ext):
            return True
    return False

def get_tdoc_link(meeting_no, tdoc_number):
    meeting_link = 'http://3gppdocsonline.com/tdocs/' + meeting_no + '/'
    tdoc_file = TDOC_ROOT + meeting_no + '/' + tdoc_number 
    for ext in ['.doc', '.docx', '.pdf', '.ppt']:
        if os.path.exists(tdoc_file + ext):
            return meeting_link + tdoc_number + ext
    return ''
    
def get_tdoc_list(meeting_no):
    tdoc_list = []
    tdoclist_path = os.path.join(BASE_DIR + '/tdoclist/')
    tdoclist_file = tdoclist_path + TDocListNames[meeting_no]
    if os.path.exists(tdoclist_file):
        wb = xlrd.open_workbook(tdoclist_file)
        sheet = wb.sheet_by_index(0)
        num_rows = sheet.nrows
        numcols = sheet.ncols

        row = 1
        while row < num_rows:
            tdoc = {}
            tdoc['number'] = sheet.row_values(row)[0]
            tdoc['title'] = sheet.row_values(row)[1]
            tdoc['source'] = sheet.row_values(row)[2]
            tdoc['type'] = sheet.row_values(row)[5]
            tdoc['agenda_item'] = sheet.row_values(row)[10]
            tdoc['ai_description'] = sheet.row_values(row)[11]
            tdoc['status'] = sheet.row_values(row)[13]
            tdoc['revision_of'] = sheet.row_values(row)[16]
            tdoc['revised_to'] = sheet.row_values(row)[17]
            tdoc['exist'] = tdoc_exist(meeting_no, tdoc['number'])
            tdoc['link'] = get_tdoc_link(meeting_no, tdoc['number'])
                
            tdoc_list.append(tdoc)
            row += 1
        
        return tdoc_list

def get_tdoc_source_options(tdoc_list):
    tdoc_source_options = [('All', 'Source (All)')]
    source_list = []
    for tdoc in tdoc_list:
        company_list = tdoc['source'].split(',')
        for company in company_list:
            if not company.lower().strip() in [x.lower() for x in source_list] and len(company)>0:
                source_list.append(company.strip())
    
    source_list = sorted(source_list)
    if len(source_list) > 0:
        for source in source_list:
            tdoc_source_tuple = (source, source)
            tdoc_source_options.append(tdoc_source_tuple)
    
    return tuple(tdoc_source_options)

def get_tdoc_agendaitem_options(tdoc_list):
    tdoc_agendaitem_options = [('All', 'Source (All)')]
    agendaitem_list = []
    temp_list = []
    ai_descriptions = {}

    for tdoc in tdoc_list:
        agendaitem = tdoc['agenda_item']
        if not agendaitem in temp_list:
            temp_list.append(agendaitem)
            ai_descriptions[agendaitem] = tdoc['ai_description']
        
    temp_list = sorted(temp_list)
    for ai in temp_list:
        ai_tuple = (ai, ai + '--' + ai_descriptions[ai])
        tdoc_agendaitem_options.append(ai_tuple)

    return tuple(tdoc_agendaitem_options)





