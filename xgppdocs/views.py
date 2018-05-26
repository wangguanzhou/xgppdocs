from django.shortcuts import render
from settings import BASE_DIR
import os
from ftplib import FTP
import xlrd
from .forms import TDocFilter

SA2Meetings = [
    {'name': 'SA2-127bis', 'time': 'May 2018', 'city': 'Newport Beach',},
    {'name': 'SA2-127', 'time': 'Apr 2018', 'city': 'Sanya',},
    {'name': 'SA2-126', 'time': 'Feb 2018', 'city': 'Montreal',},
    {'name': 'SA2-125', 'time': 'Jan 2018', 'city': 'Gothenburg',},
]

FTP_3GPP_HOST = 'ftp.3gpp.org'
SA2Path = '/tsg_sa/WG2_Arch/'
MeetingTDocPath = {
    'SA2-127bis': SA2Path+'TSGS2_127BIS_Newport_Beach/Docs/',
    'SA2-127': SA2Path+'TSGS2_127_Sanya/Docs/',
    'SA2-126': SA2Path+'TSGS2_126_Montreal/Docs/',
    'SA2-125': SA2Path+'TSGS2_125_Gothenburg/Docs/',
}
TDocListNames = {
    'SA2-127': 'TDoc_List_Meeting_SA2#127-Bis.xlsx',
    'SA2-127': 'TDoc_List_Meeting_SA2#127.xlsx',
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

    if request.POST:
        # meeting_no = request.GET['meeting']
        filter_form = TDocFilter(request.POST)
        if filter_form.is_valid():
            tdoc_filter = filter_form.cleaned_data
            context['tdoc_filter'] = tdoc_filter
        else:
            context['form_error'] = filter_form.errors
            
        return render(request, 'homepage.html', context)

    if request.GET:
        meeting_no = request.GET['meeting_no']
        context['meeting_no'] = meeting_no
        if tdoc_list_exist(meeting_no):
            tdoc_list = get_tdoc_list(meeting_no)
        else:
            return render(request, 'homepage.html', context)

        if not 'filter_button' in request.GET:
            context['tdoc_list'] = tdoc_list
           
        else:
            tdoc_filter = {}
            tdoc_filter['source'] = request.GET['tdoc_source']
            tdoc_filter['agendaitem'] = request.GET['tdoc_agendaitem']
            tdoc_filter['type'] = request.GET['tdoc_type']
            tdoc_filter['status'] = request.GET['tdoc_status']
            filtered_tdoc_list = filter_tdoc_list(tdoc_list, tdoc_filter)
            context['tdoc_list'] = filtered_tdoc_list

        tdoc_filter_form = TDocFilter()
        tdoc_filter_form.fields['tdoc_source'].choices = get_tdoc_source_options(tdoc_list)
        tdoc_filter_form.fields['tdoc_type'].choices = get_tdoc_type_options(tdoc_list)
        tdoc_filter_form.fields['tdoc_agendaitem'].choices = get_tdoc_agendaitem_options(tdoc_list)
        tdoc_filter_form.fields['tdoc_status'].choices = get_tdoc_status_options(tdoc_list)
        tdoc_filter_form.fields['meeting_no'].initial = meeting_no
        
        context['tdoc_filter'] = tdoc_filter_form
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

def filter_tdoc_list(tdoc_list, tdoc_filter):
    filtered_tdoc_list = []
    for tdoc in tdoc_list:
        bool_source = (tdoc_filter['source'] == 'All') or (tdoc_filter['source'] in [x.strip() for x in tdoc['source'].split(',')])
        bool_type = (tdoc_filter['type'] == 'All') or (tdoc_filter['type'] == tdoc['type'])
        bool_agendaitem = (tdoc_filter['agendaitem'] == 'All') or (tdoc_filter['agendaitem'] == tdoc['agenda_item'])
        bool_status = (tdoc_filter['status'] == 'All') or (tdoc_filter['status'] == tdoc['status'])
        if bool_source and bool_type and bool_agendaitem and bool_status:
            filtered_tdoc_list.append(tdoc)
    return filtered_tdoc_list
         
def get_tdoc_source_options(tdoc_list):
    tdoc_source_options = [('All', 'Source (All)')]
    source_list = []
    for tdoc in tdoc_list:
        company_list = tdoc['source'].split(',')
        for company in company_list:
            if not company.lower().strip() in [x.lower() for x in source_list] and len(company)>1:
                source_list.append(company.strip())
    
    source_list = sorted(source_list)
    if len(source_list) > 0:
        for source in source_list:
            tdoc_source_tuple = (source, source)
            tdoc_source_options.append(tdoc_source_tuple)
    
    return tuple(tdoc_source_options)

def get_tdoc_agendaitem_options(tdoc_list):
    tdoc_agendaitem_options = [('All', 'Agenda Item (All)')]
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


def get_tdoc_type_options(tdoc_list):
    tdoc_type_options = [('All', 'Type (All)')]
    temp_list = []

    for tdoc in tdoc_list:
        tdoc_type = tdoc['type']
        if not tdoc_type in temp_list:
            temp_list.append(tdoc_type)
    
    temp_list = sorted(temp_list)
    for type in temp_list:
        type_tuple = (type, type)
        tdoc_type_options.append(type_tuple)
    
    return tuple(tdoc_type_options)

def get_tdoc_status_options(tdoc_list):
    tdoc_status_options = [('All', 'Status (All)')]
    temp_list = []

    for tdoc in tdoc_list:
        tdoc_status = tdoc['status']
        if not tdoc_status in temp_list:
            temp_list.append(tdoc_status)
    
    temp_list = sorted(temp_list)
    for status in temp_list:
        status_tuple = (status, status)
        tdoc_status_options.append(status_tuple)
    
    return tuple(tdoc_status_options)




