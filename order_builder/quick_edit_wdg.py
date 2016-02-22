from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.common import Environment
from pyasm.web import Table
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from error_entry_wdg import ErrorEntryWdg
from order_builder_utils import OBScripts


class QuickEditWdg(BaseRefreshWdg):
    #This widget is used to reduce the number of elements loaded in order builder, so loading is faster.
    #It's good for making a lot of changes, especially global changes to selected elements
    #I hate this widget now, and it really doesn't seem to do much for us. Would like to take it out and modify the regular order builder to keep it's good elements
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        my.user = ''
        my.groups_str = ''
        my.disp_mode = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.small = False
        #There is no territory table in Tactic rigt now. We may want to do that in the future
        my.territory_str = 'Afghanistan|Aland Islands|Albania|Algeria|American Samoa|Andorra|Angola|Anguilla|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bonaire|Bosnia and Herzegovina|Botswana|Bouvet Island|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cambodia|Cameroon|Canada|Cantonese|Cape Verde|Cayman Islands|Central African Republic|Chad|Chile|China|Christmas Island|Cocos Islands|Colombia|Comoros|Congo|Dem. Rep. of Congo|Cook Islands|Costa Rica|Croatia|Cuba|Curacao|Cyprus|Czech|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt|El Salvador|English|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Falkland Islands|Faroe Islands|Fiji|Finland|France|French Guiana|French Polynesia|Gabon|Gambia|Georgia|Germany|Ghana|Gibraltar|Greece|Greek|Greenland|Grenada|Guadeloupe|Guam|Guatemala|Guernsey|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong|Hungary|Iceland|India|Indonesia|Iran|Iraq|Ireland|Isle of Man|Israel|Italy|Ivory Coast|Jamaica|Japan|Jersey|Jordan|Kazakhstan|Kenya|Kiribati|Kuwait|Kyrgyztan|Laos|Latin America|Latin Spanish|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luzembourg|Macao|Macedonia|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Martinique|Mauritania|Mauritius|Mayotte|Mexico|Micronesia|Moldova|Monaco|Mongolia|Montenegro|Montserrat|Morocco|Mozambique|Multi-language|Myanmar|Namibia|Nauru|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Niue|Norfolk Island|North Korea|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Palestine|Panama|Papua New Guinea|Pan-Asia|Paraguay|Peru|Philippines|Pitcairn|Poland|Portugal|Puerto Rico|Qatar|Reunion|Romania|Russia|Russian|Rwanda|St Barthelemy|St Helena|St Kitts and Nevis|St Lucia|St Martin|St Pierre and Miquelo|St Vincent and Grenadines|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Signapore|Sint Maarten|Slovakia|Slovenia|Solomon Islands|Somalia|South Africa|South Georgia and Swch Islands|South Korea|South Sudan|Spain|Sri Lanka|Sudan|Suriname|Svalbard|Swaziland|Sweden|Switzerland|Syria|Taiwan|Tajikistan|Tanzania|Thai|Thailand|Timor-Leste|Togo|Tokelau|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|UAE|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Various|Vatican|Venezuela|Vietnam|Virgin Islands|Wallis and Futuna|West Indies|Western Sahara|Yemen|Zambia|Zimbabwe'
        #There is no language table in Tactic rigt now. We may want to do that in the future
        my.language_str = 'Abkhazian|Afar|Afrikaans|Akan|Albanian|All Languages|Amharic|Arabic|Arabic - Egypt|Arabic - UAE and Lebanon|Aragonese|Aramaic|Armenian|Assamese|Avaric|Avestan|Aymara|Azerbaijani|Bahasa (Not Specified)|Bashkir|Basque|Belarusian|Bengali|Bihari languages|Bislama|Bosnian|Breton|Bulgarian|Burmese|Catalan|Catalan (Valencian)|Central Khmer|Chamorro|Chechen|Chichewa (Chewa, Nyanja)|Chinese (Cantonese)|Chinese (Mandarin - Not Specified)|Chinese (Mandarin - PRC)|Chinese (Mandarin - Taiwan)|Chinese Simplified Characters|Chinese Simplified Characters - Malaysia|Chinese Simplified Characters - PRC|Chinese Simplified Characters - Singapore|Chinese Traditional Characters|Chinese Traditional Characters - Hong Kong|Chinese Traditional Characters - Taiwan|Chuvash|Cornish|Corsican|Cree|Croatian|Czech|Danish|Dari|Divehi (Dhivehi, Maldivian)|Dutch|Dzongkha|English|English - Australian|English - British|Esperanto|Estonian|Ewe|Faroese|Farsi (Persian)|Fijian|Finnish|Flemish|French (Not Specified)|French - Canadian (Quebecois)|French - France|Fulah|Gaelic (Scottish Gaelic)|Galician|Georgian|German|German - Austrian|German - Swiss/Alsatian|Greek - Modern|Guarani|Gujarati|Haitian (Haitian Creole)|Hausa|Hawaiian|Hebrew|Herero|Hindi|Hiri Motu|Hungarian|Icelandic|Ido|Indonesian Bahasa|Interlingua (International Auxiliary Language Association)|Interlingue (Occidental)|Inuktitut|Inupiaq|Italian|Japanese|Javanese|Kalaallisut (Greenlandic)|Kannada|Kanuri|Kashmiri|Kazakh|Kikuyu (Gikuyu)|Kinyarwanda|Kirghiz (Kyrgyz)|Komi|Kongo|Korean|Kuanyama (Kwanyama)|Kurdish|Lao|Latin|Latvian|Limburgan (Limburger, Limburgish)|Lingala|Lithuanian|Luba-Katanga|Luxembourgish (Letzeburgesch)|MOS (no audio)|Macedonian|Malagasy|Malay Bahasa|Malayalam|Maltese|Maori|Marathi|Marshallese|Mauritian Creole|Mayan|Moldavian|Mongolian|Nauru|Navajo (Navaho)|Ndebele - North|Ndebele - South|Ndonga|Nepali|No Audio|Northern Sami|Norwegian|Occitan|Ojibwa|Oriya|Oromo|Ossetian (Ossetic)|Palauan|Pali|Panjabi (Punjabi)|Polish|Polynesian|Portuguese (Not Specified)|Portuguese - Brazilian|Portuguese - European|Pushto (Pashto)|Quechua|Romanian|Romanian (Moldavian)|Romansh|Rundi|Russian|Samoan|Sango|Sanskrit|Sardinian|Sepedi|Serbian|Serbo-Croatian|Setswana|Shona|Sichuan Yi (Nuosu)|Sicilian|Silent|Sindhi|Sinhala (Sinhalese)|Slavic|Slovak|Slovenian|Somali|Sotho, Sesotho|Spanish (Not Specified)|Spanish - Argentinian|Spanish - Castilian|Spanish - Latin American|Spanish - Mexican|Sudanese|Swahili|Swati|Swedish|Tagalog|Tahitian|Taiwanese (Min Nah)|Tajik|Tamil|Tatar|Telugu|Tetum|Textless|Thai|Tibetan|Tigrinya|Tok Pisin|Tongan|Tsonga|Turkish|Turkmen|Tuvaluan|Twi|Uighur (Uyghur)|Ukrainian|Unavailable|Unknown|Unknown|Urdu|Uzbek|Valencian|Venda|Vietnamese|Volapuk|Walloon|Welsh|Western Frisian|Wolof|Xhosa|Yiddish|Yoruba|Zhuang (Chuang)|Zulu'

    def get_toggle_select_check_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                           var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                           order_sk = '%s';
                           top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           var curr_val = bvr.src_el.getAttribute('checked');
                           image = '';
                           if(curr_val == 'false'){
                               curr_val = false;
                               image = not_checked_img;
                           }else if(curr_val == 'true'){
                               curr_val = true;
                               image = checked_img;
                           }
                           checks = top_el.getElementsByClassName('ob_selector');
                           for(var r = 0; r < checks.length; r++){
                               check_code = checks[r].getAttribute('value_field');
                               parent_table_class = checks[r].getAttribute('parent_table');
                               parent_table = top_el.getElementsByClassName(parent_table_class)[0];
                               new_color = '';
                               if(curr_val){
                                   new_color = checks[r].getAttribute('selected_color');
                               }else{
                                   new_color = checks[r].getAttribute('normal_color');
                               }
                               parent_table.style.backgroundColor = new_color;
                               checks[r].setAttribute('checked',curr_val);
                               checks[r].innerHTML = image;
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk)}
        return behavior

    def get_assigned_group_select(my, assigned, name):
        #Make the select element for groups
        groups_expr = "@GET(sthpw/login_group['login_group','not in','user|client|compression supervisor|edit supervisor|machine room supervisor|media vault supervisor|qc supervisor|sales supervisor|scheduling supervisor|streamz|executives|admin|management|office employees|it'].login_group)"
        groups = my.server.eval(groups_expr)
        group_sel = SelectWdg(name)
        if len(groups) > 0:
            group_sel.append_option('--Select--','')
            if assigned:
                group_sel.set_value(assigned)
            else:
                group_sel.set_value('')
            for group in groups:
                group_sel.append_option(group,group)
        return group_sel

    def get_assigned_select(my, assigned):
        #Make the select element for workers
        workers_expr = "@GET(sthpw/login['location','internal']['license_type','user'].login)"
        workers = my.server.eval(workers_expr)
        work_sel = SelectWdg('task_assigned_select')
        if len(workers) > 0:
            work_sel.append_option('--Select--','')
            if assigned:
                work_sel.set_value(assigned)
            else:
                work_sel.set_value('')
            for worker in workers:
                work_sel.append_option(worker,worker)
        return work_sel

    def get_display(my):
        my.order_sk = my.kwargs.get('order_sk')
        order_code = my.order_sk.split('code=')[1]
        my.groups_str = None
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode')
            if my.disp_mode == 'Small':
                my.small = True
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            user_group_names = Environment.get_group_names()
            for mg in user_group_names:
                if my.groups_str == '':
                    my.groups_str = mg
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg)
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
            if main_obj.get('classification') in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        # Get the javascript functions
        obs = OBScripts(order_sk=my.order_sk,user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
        table = Table()
        table.add_attr('class','qe_top_%s' % my.order_sk)
        table.add_attr('width','100%s' % '%')
        table.add_row()
        type_checks_tbl = Table()
        long_row = type_checks_tbl.add_row()
        long_row.add_attr('width','100%s' % '%')
        title_check = CustomCheckboxWdg(name='qe_titles_%s' % my.order_sk,value_field='title',checked='false',dom_class='quick_edit_selector')

        type_checks_tbl.add_cell(title_check)
        type_checks_tbl.add_cell('Titles')

        proj_check = CustomCheckboxWdg(name='qe_projects_%s' % my.order_sk,value_field='projects',checked='false',dom_class='quick_edit_selector')

        type_checks_tbl.add_cell(proj_check)
        type_checks_tbl.add_cell('Projects')

        wo_check = CustomCheckboxWdg(name='qe_work_orders_%s' % my.order_sk,value_field='work orders',checked='false',dom_class='quick_edit_selector')
        type_checks_tbl.add_cell(wo_check)
        wo = type_checks_tbl.add_cell('Work Orders')
        wo.add_attr('nowrap','nowrap')

        eq_check = CustomCheckboxWdg(name='qe_equipment_%s' % my.order_sk,value_field='equipment',checked='false',dom_class='quick_edit_selector')

        type_checks_tbl.add_cell(eq_check)
        type_checks_tbl.add_cell('Equipment')

        group_selector = my.get_assigned_group_select(None,'group_selector')
        group_selector.add_behavior(obs.get_select_checks_by_group_behavior())
        sbd0 = type_checks_tbl.add_cell('&nbsp;&nbsp;&nbsp;')
        sbd = type_checks_tbl.add_cell('Select by Dept:')
        sbd.add_attr('nowrap','nowrap')
        type_checks_tbl.add_cell(group_selector)

        tog_check = CustomCheckboxWdg(name='qe_toggler',additional_js=my.get_toggle_select_check_behavior(),value_field='toggler',id='selection_toggler',checked='false')

        last_cell = type_checks_tbl.add_cell(tog_check)
        last_cell.add_attr('width', '100%s' % '%')
        last_cell.add_attr('align','right')
        lc1 = type_checks_tbl.add_cell('Select/Deselect All In Table')
        lc1.add_attr('width', '100%s' % '%')
        lc1.add_attr('align','right')
        lc1.add_attr('nowrap','nowrap')

        long_cell = table.add_cell(type_checks_tbl)
        long_cell.add_attr('colspan','8')

        table.add_row()
        table.add_cell('Platform: ')
        # Get the list of platforms from the db
        # Create the platform select wdg
        platforms = my.server.eval("@GET(twog/platform['@ORDER_BY','name'].name)")
        platform_sel = SelectWdg('platform_sel_%s' % my.order_sk)
        platform_sel.append_option('--Select--','--Select--')
        for platform in platforms:
            platform_sel.append_option(platform, platform)
        table.add_cell(platform_sel)

        # Create the territory select wdg
        territories = my.territory_str.split('|')
        territory_sel = SelectWdg('territory_sel_%s' % my.order_sk)
        territory_sel.append_option('--Select--','--Select--')
        for territory in territories:
            territory_sel.append_option(territory, territory)
        table.add_cell('Territory: ')
        table.add_cell(territory_sel)

        # Create the languages select wdg
        languages = my.language_str.split('|')
        language_sel = SelectWdg('language_sel_%s' % my.order_sk)
        language_sel.append_option('--Select--','--Select--')
        for language in languages:
            language_sel.append_option(language, language)
        table.add_cell('Language: ')
        table.add_cell(language_sel)

        # Create calendar input for start date
        sd = table.add_cell('Start Date: ')
        sd.add_attr('nowrap','nowrap')
        start = CalendarInputWdg("qe_start_date_%s" % my.order_sk)
        start.set_option('show_activator', True)
        start.set_option('show_confirm', False)
        start.set_option('show_text', True)
        start.set_option('show_today', False)
        start.set_option('read_only', False)
        start.get_top().add_style('width: 150px')
        start.set_persist_on_submit()
        start_date = table.add_cell(start)
        start_date.add_attr('nowrap', 'nowrap')

        # Create calendar input for due date
        dd = table.add_cell('Due Date: ')
        dd.add_attr('nowrap', 'nowrap')
        due = CalendarInputWdg("qe_due_date_%s" % my.order_sk)
        due.set_option('show_activator', True)
        due.set_option('show_confirm', False)
        due.set_option('show_text', True)
        due.set_option('show_today', False)
        due.set_option('read_only', False)
        due.get_top().add_style('width: 150px')
        due.set_persist_on_submit()
        due_date = table.add_cell(due)
        due_date.add_attr('nowrap', 'nowrap')

        table.add_cell('Priority: ')
        table.add_cell('<input type="text" name="qe_priority_%s"/>' % my.order_sk)

        table.add_row()

        # Statuses should pull from the database soon, so I won't have to adjust this list every time a new status is added or removed
        statuses = ['Pending', 'Ready', 'On Hold', 'Client Response', 'Fix Needed', 'Rejected', 'In Progress',
                    'DR In Progress', 'Amberfin01 In Progress', 'Amberfin02 In Progress', 'BATON In Progress',
                    'Export In Progress', 'Need Buddy Check', 'Buddy Check In Progress', 'Completed']
        status_sel = SelectWdg('eq_status_%s' % my.order_sk)
        status_sel.append_option('--Select--','--Select--')
        for status in statuses:
            status_sel.append_option(status, status)
        table.add_cell('Status: ')
        table.add_cell(status_sel)

        assigned_group_select = my.get_assigned_group_select(None, 'assigned_group_select')
        ag = table.add_cell('Assigned Group: ')
        ag.add_attr('nowrap', 'nowrap')
        table.add_cell(assigned_group_select)

        assigned_select = my.get_assigned_select(None)
        ad = table.add_cell('Assigned: ')
        ad.add_attr('nowrap', 'nowrap')
        table.add_cell(assigned_select)

        ewh = table.add_cell('Estimated Work Hours: ')
        ewh.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ewh_%s"/>' % my.order_sk)

        table.add_row()

        ed = table.add_cell('Expected Duration: ')
        ed.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ex_dur_%s"/>' % my.order_sk)

        exq = table.add_cell('Expected Quantity: ')
        exq.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ex_quan_%s"/>' % my.order_sk)

        #Submit button applies changes to everything in the order builder that is selected
        submit_button = table.add_cell('<input type="button" name="submit_button" value="Apply Changes"/>')
        submit_button.add_behavior(obs.get_submit_quick_changes())
        #Add equipment to all work orders that are selected
        add_eq_button = table.add_cell('<input type="button" name="add_eq_button" value="Edit Equipment"/>')
        add_eq_button.add_behavior(obs.get_eq_edit_behavior())
        last_chunk = table.add_cell(' ')
        last_chunk.add_attr('width', '100%')
        open_errors = table.add_cell('<u>Document Errors</u>')
        open_errors.add_attr('name','qe_error_opener_%s' % my.order_sk)
        open_errors.add_style('cursor: pointer;')
        open_errors.add_behavior(obs.get_open_errors_behavior())
        # Button to delete selected objects
        delete_button = table.add_cell('<input type="button" name="delete_button" value="Delete Selected"/>')
        delete_button.add_behavior(obs.get_qe_delete())

        # This is where the scheduler can enter production errors. It is hidden until "Document Errors" is clicked
        errors_row = table.add_row()
        errors_row.add_attr('class','qe_errors_row_%s' % my.order_sk)
        errors_row.add_style('display: none;')
        errors_wdg = ErrorEntryWdg(order_sk=my.order_sk,code='NOCODE',user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
        errors_cell = table.add_cell(errors_wdg)
        errors_cell.add_attr('colspan','10')
        return table
