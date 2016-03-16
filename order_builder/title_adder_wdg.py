from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import CalendarInputWdg, ActionButtonWdg

from pyasm.common import Environment
from pyasm.biz import *
from pyasm.web import Table
from pyasm.widget import SelectWdg
from pyasm.search import Search

from common_tools.common_functions import fix_date


class TitleAdderWdg(BaseRefreshWdg):

    def init(my):
        my.title = 'Equipment Used'
        my.sk = ''
        my.code = ''
        my.user = Environment.get_user_name()
        my.parent_sk = ''
        my.order_sk = ''
        my.order_sid = ''
        my.client_code = ''
        my.formats = ['Electronic/File', 'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ProdSetting.get_seq_by_key('frame_rates')
        my.aspect_ratios = ['16x9 1.33', '16x9 1.33 Pan & Scan', '16x9 1.78 Anamorphic', '16x9 1.78 Full Frame',
                            '16x9 1.85 Letterbox', '16x9 1.85 Matted', '16x9 1.85 Matted Anamorphic', '16x9 2.20',
                            '16x9 2.20 Letterbox', '16x9 2.35 Anamorphic', '16x9 2.35 Letterbox', '16x9 2.40 Letterbox',
                            '16x9 2.55 Letterbox', '4x3 1.33 Full Frame', '4x3 1.78 Letterbox', '4x3 1.85 Letterbox',
                            '4x3 2.35 Letterbox', '4x3 2.40 Letterbox']
        my.standards = ['625', '525', '720', '1080 (4:4:4)', '1080', 'PAL', 'NTSC']

    def get_display(my):
        my.client_code = str(my.kwargs.get('client_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.order_sid = str(my.kwargs.get('order_sid'))
        order_code = my.order_sk.split('code=')[1]
        order_search = Search("twog/order")
        order_search.add_filter('code',order_code)
        the_order = order_search.get_sobject()

        table = Table()
        table.add_attr('class', 'title_adder_top_%s' % my.order_sk)
        table.add_row()
        table.add_cell('Title: ')
        cell1 = table.add_cell('<input class="tadd_title" type="text"/>')
        cell1.add_attr('colspan','5')
        cell1.add_attr('align','left')

        table.add_row()
        empt = table.add_cell(' ')
        beg = table.add_cell('Range Begin')
        empt = table.add_cell(' ')
        end = table.add_cell('Range End')
        formatter = table.add_cell('# Formatter')
        empt = table.add_cell(' ')
        beg.add_attr('nowrap', 'nowrap')
        beg.add_attr('valign', 'bottom')
        end.add_attr('nowrap', 'nowrap')
        end.add_attr('valign', 'bottom')
        formatter.add_attr('nowrap', 'nowrap')
        formatter.add_attr('valign', 'bottom')
        beg.add_style('font-size: 50%;')
        end.add_style('font-size: 50%;')
        formatter.add_style('font-size: 50%;')
        singl = table.add_cell('Single Episode Name, or Comma Seperated Episode Names')
        singl.add_attr('valign', 'bottom')
        singl.add_style('font-size: 50%;')
        table.add_row()
        table.add_cell('Episode: ')
        table.add_cell('<input class="tadd_epi_range_1" type="text" style="width: 35px;"/>')
        ctr = table.add_cell(' - ')
        ctr.add_attr('align', 'center')
        table.add_cell('<input class="tadd_epi_range_2" type="text" style="width: 35px;"/>')
        table.add_cell('<input class="tadd_episode_format" type="text" style="width: 70px;"/>')
        table.add_cell(' OR ')
        table.add_cell('<input class="tadd_epi_name" type="text" style="width: 200px;"/>')
        #There is no territory table in Tactic rigt now. We may want to do that in the future
        territories_str = 'Afghanistan|Aland Islands|Albania|Algeria|American Samoa|Andorra|Angola|Anguilla|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bonaire|Bosnia and Herzegovina|Botswana|Bouvet Island|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cambodia|Cameroon|Canada|Cantonese|Cape Verde|Cayman Islands|Central African Republic|Chad|Chile|China|Christmas Island|Cocos Islands|Colombia|Comoros|Congo|Dem. Rep. of Congo|Cook Islands|Costa Rica|Croatia|Cuba|Curacao|Cyprus|Czech|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt|El Salvador|English|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Falkland Islands|Faroe Islands|Fiji|Finland|France|French Guiana|French Polynesia|Gabon|Gambia|Georgia|Germany|Ghana|Gibraltar|Greece|Greek|Greenland|Grenada|Guadeloupe|Guam|Guatemala|Guernsey|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong|Hungary|Iceland|India|Indonesia|Iran|Iraq|Ireland|Isle of Man|Israel|Italy|Ivory Coast|Jamaica|Japan|Jersey|Jordan|Kazakhstan|Kenya|Kiribati|Kuwait|Kyrgyztan|Laos|Latin America|Latin Spanish|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luzembourg|Macao|Macedonia|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Martinique|Mauritania|Mauritius|Mayotte|Mexico|Micronesia|Moldova|Monaco|Mongolia|Montenegro|Montserrat|Morocco|Mozambique|Multi-language|Myanmar|Namibia|Nauru|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Niue|Norfolk Island|North Korea|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Palestine|Panama|Papua New Guinea|Pan-Asia|Paraguay|Peru|Philippines|Pitcairn|Poland|Portugal|Puerto Rico|Qatar|Reunion|Romania|Russia|Russian|Rwanda|St Barthelemy|St Helena|St Kitts and Nevis|St Lucia|St Martin|St Pierre and Miquelo|St Vincent and Grenadines|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Signapore|Sint Maarten|Slovakia|Slovenia|Solomon Islands|Somalia|South Africa|South Georgia and Swch Islands|South Korea|South Sudan|Spain|Sri Lanka|Sudan|Suriname|Svalbard|Swaziland|Sweden|Switzerland|Syria|Taiwan|Tajikistan|Tanzania|Thai|Thailand|Timor-Leste|Togo|Tokelau|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|UAE|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Various|Vatican|Venezuela|Vietnam|Virgin Islands|Wallis and Futuna|West Indies|Western Sahara|Yemen|Zambia|Zimbabwe'
        territories = territories_str.split('|')
        territory_sel = SelectWdg('tadd_territory')
        territory_sel.append_option('--Select--', '--Select--')
        for terr in territories:
            territory_sel.append_option(terr, terr)
        #There is no language table in Tactic. We may want to change that in the future.
        language_str = 'Abkhazian|Afar|Afrikaans|Akan|Albanian|All Languages|Amharic|Arabic|Arabic - Egypt|Arabic - UAE and Lebanon|Aragonese|Aramaic|Armenian|Assamese|Avaric|Avestan|Aymara|Azerbaijani|Bahasa (Not Specified)|Bashkir|Basque|Belarusian|Bengali|Bihari languages|Bislama|Bosnian|Breton|Bulgarian|Burmese|Catalan|Catalan (Valencian)|Central Khmer|Chamorro|Chechen|Chichewa (Chewa, Nyanja)|Chinese (Cantonese)|Chinese (Mandarin - Not Specified)|Chinese (Mandarin - PRC)|Chinese (Mandarin - Taiwan)|Chinese Simplified Characters|Chinese Simplified Characters - Malaysia|Chinese Simplified Characters - PRC|Chinese Simplified Characters - Singapore|Chinese Traditional Characters|Chinese Traditional Characters - Hong Kong|Chinese Traditional Characters - Taiwan|Chuvash|Cornish|Corsican|Cree|Croatian|Czech|Danish|Dari|Divehi (Dhivehi, Maldivian)|Dutch|Dzongkha|English|English - Australian|English - British|Esperanto|Estonian|Ewe|Faroese|Farsi (Persian)|Fijian|Finnish|Flemish|French (Not Specified)|French - Canadian (Quebecois)|French - France|Fulah|Gaelic (Scottish Gaelic)|Galician|Georgian|German|German - Austrian|German - Swiss/Alsatian|Greek - Modern|Guarani|Gujarati|Haitian (Haitian Creole)|Hausa|Hawaiian|Hebrew|Herero|Hindi|Hiri Motu|Hungarian|Icelandic|Ido|Indonesian Bahasa|Interlingua (International Auxiliary Language Association)|Interlingue (Occidental)|Inuktitut|Inupiaq|Italian|Japanese|Javanese|Kalaallisut (Greenlandic)|Kannada|Kanuri|Kashmiri|Kazakh|Kikuyu (Gikuyu)|Kinyarwanda|Kirghiz (Kyrgyz)|Komi|Kongo|Korean|Kuanyama (Kwanyama)|Kurdish|Lao|Latin|Latvian|Limburgan (Limburger, Limburgish)|Lingala|Lithuanian|Luba-Katanga|Luxembourgish (Letzeburgesch)|MOS (no audio)|Macedonian|Malagasy|Malay Bahasa|Malayalam|Maltese|Maori|Marathi|Marshallese|Mauritian Creole|Mayan|Moldavian|Mongolian|Nauru|Navajo (Navaho)|Ndebele - North|Ndebele - South|Ndonga|Nepali|No Audio|Northern Sami|Norwegian|Occitan|Ojibwa|Oriya|Oromo|Ossetian (Ossetic)|Palauan|Pali|Panjabi (Punjabi)|Polish|Polynesian|Portuguese (Not Specified)|Portuguese - Brazilian|Portuguese - European|Pushto (Pashto)|Quechua|Romanian|Romanian (Moldavian)|Romansh|Rundi|Russian|Samoan|Sango|Sanskrit|Sardinian|Sepedi|Serbian|Serbo-Croatian|Setswana|Shona|Sichuan Yi (Nuosu)|Sicilian|Silent|Sindhi|Sinhala (Sinhalese)|Slavic|Slovak|Slovenian|Somali|Sotho, Sesotho|Spanish (Not Specified)|Spanish - Argentinian|Spanish - Castilian|Spanish - Latin American|Spanish - Mexican|Sudanese|Swahili|Swati|Swedish|Tagalog|Tahitian|Taiwanese (Min Nah)|Tajik|Tamil|Tatar|Telugu|Tetum|Textless|Thai|Tibetan|Tigrinya|Tok Pisin|Tongan|Tsonga|Turkish|Turkmen|Tuvaluan|Twi|Uighur (Uyghur)|Ukrainian|Unavailable|Unknown|Unknown|Urdu|Uzbek|Valencian|Venda|Vietnamese|Volapuk|Walloon|Welsh|Western Frisian|Wolof|Xhosa|Yiddish|Yoruba|Zhuang (Chuang)|Zulu'

        languages = language_str.split('|')
        language_sel = SelectWdg('tadd_language')
        language_sel.append_option('--Select--', '--Select--')
        for language in languages:
            language_sel.append_option(language, language)

        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()

        pipe_search = Search("sthpw/pipeline")
        pipe_search.add_filter('search_type', 'twog/title')
        pipelines = pipe_search.get_sobjects()
        client_pull = SelectWdg('tadd_client_pull')
        client_name = ''
        if len(clients) > 0:
            client_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for client in clients:
                client_pull.append_option(client.get_value('name'), '%sXsX%s' % (client.get_value('code'),client.get_value('name')))
                if client.get_value('code') == my.client_code:
                    client_name = client.get_value('name')
                    client_name_pull = '%sXsX%s' % (client.get_value('code'), client.get_value('name'))
                    client_pull.set_value(client_name_pull)
        client_pull.add_behavior(get_client_change_behavior(my.order_sk))
        platform_search = Search("twog/platform")
        platform_search.add_order_by('name desc')
        outlet_list = platform_search.get_sobjects()
        outlet_pull = SelectWdg('tadd_outlet_pull')
        outlet_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for outlet in outlet_list:
            outlet_pull.append_option(outlet.get_value('name'), outlet.get_value('name'))
        pipe_pull = SelectWdg('tadd_pipe_pull')
        if len(pipelines) > 0:
            pipe_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for pipe in pipelines:
                if not pipe.get_value('hide'):
                    if pipe.get_value('code').split('_')[0] == client_name:
                        pipe_pull.append_option(pipe.get_value('code'), pipe.get_value('code'))
            for pipe in pipelines:
                if not pipe.get_value('hide'):
                    if pipe.get_value('code').split('_')[0] != client_name:
                        pipe_pull.append_option(pipe.get_value('code'), pipe.get_value('code'))
        pipe_pull.add_behavior(get_pipeline_change_behavior(my.order_sk))


        dlv_standard_pull = SelectWdg('tadd_deliverable_standard')
        dlv_standard_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for s in my.standards:
            dlv_standard_pull.append_option(s, s)
        dlv_format_pull = SelectWdg('tadd_deliverable_format')
        dlv_format_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for f in my.formats:
            dlv_format_pull.append_option(f, f)
        dlv_aspect_ratio_pull = SelectWdg('tadd_deliverable_aspect_ratio')
        dlv_aspect_ratio_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for a in my.aspect_ratios:
            dlv_aspect_ratio_pull.append_option(a, a)
        dlv_frame_rate_pull = SelectWdg('tadd_deliverable_frame_rate')
        dlv_frame_rate_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for f in my.frame_rates:
            dlv_frame_rate_pull.append_option(f, f)

        status_triggers_pull = SelectWdg('tadd_status_triggers')
        for f in ['Yes', 'No']:
            status_triggers_pull.append_option(f, f)

        priority_triggers_pull = SelectWdg('tadd_priority_triggers')
        for f in ['Yes', 'No']:
            priority_triggers_pull.append_option(f, f)

        table.add_row()
        t1 = table.add_cell('Territory: ')
        t2 = table.add_cell(territory_sel)
        t1.add_attr('align', 'left')
        t2.add_attr('colspan', '6')
        t2.add_attr('align', 'left')

        table.add_row()
        t1 = table.add_cell('Language: ')
        t2 = table.add_cell(language_sel)
        t1.add_attr('align', 'left')
        t2.add_attr('colspan', '6')
        t2.add_attr('align', 'left')

        table.add_row()
        c1 = table.add_cell('Client: ')
        c2 = table.add_cell(client_pull)
        c1.add_attr('align', 'left')
        c2.add_attr('colspan', '6')
        c2.add_attr('align', 'left')

        table.add_row()
        o1 = table.add_cell('Platform: ')
        o2 = table.add_cell(outlet_pull)
        o1.add_attr('align', 'left')
        o2.add_attr('colspan', '6')
        o2.add_attr('align', 'left')

        table.add_row()
        r1 = table.add_cell('Title Id Num: ')
        r2 = table.add_cell('<input type="text" class="tadd_title_id_number"/>')
        r1.add_attr('align', 'left')
        r2.add_attr('colspan', '6')
        r2.add_attr('align', 'left')

        table.add_row()
        w1 = table.add_cell('Total Program Run Time: ')
        w2 = table.add_cell('<input type="text" class="tadd_total_program_run_time"/>')
        w1.add_attr('align', 'left')
        w2.add_attr('colspan', '6')
        w2.add_attr('align', 'left')

        table.add_row()
        z1 = table.add_cell('Total Run Time w/ Textless: ')
        z2 = table.add_cell('<input type="text" class="tadd_total_run_time_with_textless"/>')
        z1.add_attr('align', 'left')
        z2.add_attr('colspan', '6')
        z2.add_attr('align', 'left')

        table.add_row()
        p1 = table.add_cell('Pipeline: ')
        p2 = table.add_cell(pipe_pull)
        p1.add_attr('align', 'left')
        p2.add_attr('colspan', '6')
        p2.add_attr('align', 'left')

        table.add_row()
        sd = table.add_cell('Start Date: ')
        sd.add_attr('nowrap', 'nowrap')
        start = CalendarInputWdg("tadd_start_date")
        if the_order.get_value('start_date') not in [None,'']:
            start.set_option('default', fix_date(the_order.get_value('start_date')))
        start.set_option('show_activator', True)
        start.set_option('show_confirm', False)
        start.set_option('show_text', True)
        start.set_option('show_today', False)
        start.set_option('read_only', False)
        start.get_top().add_style('width: 150px')
        start.set_persist_on_submit()
        start_date = table.add_cell(start)
        start_date.add_attr('colspan', '7')
        start_date.add_attr('nowrap', 'nowrap')

        table.add_row()
        ed = table.add_cell('Due Date: ')
        ed.add_attr('nowrap','nowrap')
        end = CalendarInputWdg("tadd_due_date")
        if the_order.get_value('due_date') not in [None,'']:
            end.set_option('default', fix_date(the_order.get_value('due_date')))
        end.set_option('show_activator', True)
        end.set_option('show_confirm', False)
        end.set_option('show_text', True)
        end.set_option('show_today', False)
        end.set_option('read_only', False)
        end.get_top().add_style('width: 150px')
        end.set_persist_on_submit()
        end_date = table.add_cell(end)
        end_date.add_attr('colspan', '7')
        end_date.add_attr('nowrap', 'nowrap')

        table.add_row()
        rm = table.add_cell('Revenue Month: ')
        rm.add_attr('nowrap','nowrap')
        rem = CalendarInputWdg("tadd_rm_date")
        if the_order.get_value('expected_delivery_date') not in [None,'']:
            rem.set_option('default', fix_date(the_order.get_value('expected_delivery_date')))
        rem.set_option('show_activator', True)
        rem.set_option('show_confirm', False)
        rem.set_option('show_text', True)
        rem.set_option('show_today', False)
        rem.set_option('read_only', False)
        rem.get_top().add_style('width: 150px')
        rem.set_persist_on_submit()
        rem_date = table.add_cell(rem)
        rem_date.add_attr('colspan', '7')
        rem_date.add_attr('nowrap', 'nowrap')

        table.add_row()
        r8 = table.add_cell('Expected Price: ')
        r9 = table.add_cell('<input type="text" class="tadd_expected_price"/>')
        r8.add_attr('align', 'left')
        r9.add_attr('colspan', '6')
        r9.add_attr('align', 'left')

        table.add_row()
        taa = table.add_cell('Description')
        taa.add_attr('valign', 'top')
        ta1 = table.add_cell('<textarea cols="50" rows="10" class="tadd_description"></textarea>')
        ta1.add_attr('colspan', '6')

        table.add_row()
        s1 = table.add_cell('Deliverable Standard: ')
        s2 = table.add_cell(dlv_standard_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Aspect Ratio: ')
        s2 = table.add_cell(dlv_aspect_ratio_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Frame Rate: ')
        s2 = table.add_cell(dlv_frame_rate_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Format: ')
        s2 = table.add_cell(dlv_format_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Status Triggers?: ')
        s2 = table.add_cell(status_triggers_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Priority Triggers?: ')
        s2 = table.add_cell(priority_triggers_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        tca = table.add_cell('Deliverable Specs')
        tca.add_attr('valign', 'top')
        ta8 = table.add_cell('<textarea cols="50" rows="10" class="tadd_delivery_specs"></textarea>')
        ta8.add_attr('colspan', '6')

        table.add_row()
        table.add_cell('Keywords')
        ta2 = table.add_cell('<textarea cols="50" class="tadd_keywords"></textarea>')
        ta2.add_attr('colspan', '6')

        go_butt = ActionButtonWdg(tip='Create', title='Create')
        go_butt.add_behavior(get_create_titles_behavior(my.order_sk, my.order_sid, my.user))
        table.add_row()
        bottom_butt = table.add_cell(go_butt)
        bottom_butt.add_attr('colspan', '7')
        bottom_butt.add_attr('align', 'center')

        return table


def get_client_change_behavior(order_sk):
    behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''
                    try{
                      //alert('m64');
                      var server = TacticServerStub.get();
                      var order_sk = '%s';
                      client = bvr.src_el.value.split('XsX')[1];
                      var title_top_el = document.getElementsByClassName('title_adder_top_' + order_sk)[0];
                      var sels = title_top_el.getElementsByTagName('select');
                      pipe_sel = '';
                      for(var r = 0; r < sels.length; r++){
                          if(sels[r].getAttribute('name') == 'tadd_pipe_pull'){
                              pipe_sel = sels[r];
                          }
                      }
                      pipe_opts = pipe_sel.innerHTML;
                      opts = pipe_opts.split('<option ');
                      top_opt = '<option ' + opts[1];
                      top_opts = [];
                      after_opts = [];
                      for(var r = 2; r < opts.length; r++){
                          if(opts[r] != ''){
                                  boo = true;
                                  after_val_s = opts[r].split('value="');
                                  if(after_val_s.length > 1){
                                      after_val = after_val_s[1];
                                      bef_quo = after_val.split('"')[0];
                                      bef_und = bef_quo.split('_')[0];
                                      if(bef_und == client){
                                          top_opts.push('<option ' + opts[r]);
                                      }else{
                                          after_opts.push('<option ' + opts[r]);
                                      }
                                  }else{
                                      after_opts.push('<option ' + opts[r]);
                                  }
                          }
                      }
                      new_inner = top_opt;
                      for(var r = 0 ; r < top_opts.length; r++){
                          new_inner = new_inner + top_opts[r];
                      }
                      for(var r = 0 ; r < after_opts.length; r++){
                          new_inner = new_inner + after_opts[r];
                      }

                      pipe_sel.innerHTML = new_inner;
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % order_sk}
    return behavior


def get_pipeline_change_behavior(order_sk):
    behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      var order_sk = '%s';
                      pipeline_code = bvr.src_el.value;
                      pipeline_deliv_specs = server.eval("@GET(sthpw/pipeline['code','" + pipeline_code + "'].delivery_specs)")[0];
                      var title_top_el = document.getElementsByClassName('title_adder_top_' + order_sk)[0];
                      dspecs = title_top_el.getElementsByClassName('tadd_delivery_specs')[0];
                      dspecs.innerHTML = pipeline_deliv_specs;
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % order_sk}
    return behavior


def get_create_titles_behavior(order_sk, order_sid, login):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
function oc(a){
    var o = {};
    for(var i=0;i<a.length;i++){
        o[a[i]]='';
    }
    return o;
}
function trim(stringToTrim) {
    return stringToTrim.replace(/^\s+|\s+$/g,"");
}
function format_replace(replacer, replace_char, format_string) {
    new_str = '';
    for(var r = 0; r < format_string.length; r++){
        if(format_string[r] == replace_char){
            new_str = new_str + replacer;
        }else{
            new_str = new_str + format_string[r];
        }
    }
    if(new_str == format_string){
        new_str = replacer;
    }
    return new_str;
}
try{

    spt.app_busy.show('Creating Title(s)...');
    var server = TacticServerStub.get();
    var order_sk = '%s';
    var order_sid = '%s';
    var login = '%s';

    var order_code = order_sk.split('code=')[1];
    var order_obj = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
    //alert('create');
    var order_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
    var allowed_titles = order_el.getAttribute('allowed_titles');
    if(allowed_titles == 'NOTHING|NOTHING'){
      allowed_titles = '';
    }
    allowed_titles_arr = allowed_titles.split('|')
    var top_el = document.getElementsByClassName('title_adder_top_' + order_sk)[0];
    var loader_cell = document.getElementsByClassName('cell_' + order_sk)[0];
    var title =  top_el.getElementsByClassName('tadd_title')[0];
    var range1 = top_el.getElementsByClassName('tadd_epi_range_1')[0];
    var range2 = top_el.getElementsByClassName('tadd_epi_range_2')[0];
    var formatter_el = top_el.getElementsByClassName('tadd_episode_format')[0];
    var epi_name = top_el.getElementsByClassName('tadd_epi_name')[0];
    var title_id_num_el = top_el.getElementsByClassName('tadd_title_id_number')[0];
    var total_program_run_time_el = top_el.getElementsByClassName('tadd_total_program_run_time')[0];
    var total_runtime_with_textless_el = top_el.getElementsByClassName('tadd_total_run_time_with_textless')[0];
    var expected_price_el = top_el.getElementsByClassName('tadd_expected_price')[0];
    var sels = top_el.getElementsByTagName('select');
    var client_pull = '';
    var pipe_pull = '';
    var terr_pull = '';
    var outlet_pull = '';
    var language_pull = '';
    var deliverable_standard = '';
    var deliverable_frame_rate = '';
    var deliverable_aspect_ratio = '';
    var deliverable_format = '';
    var status_triggers = '';
    var priority_triggers = '';
    for(var r = 0; r < sels.length; r++){
      if(sels[r].name == 'tadd_client_pull'){
          client_pull = sels[r];
      }else if(sels[r].name == 'tadd_pipe_pull'){
          pipe_pull = sels[r];
      }else if(sels[r].name == 'tadd_territory'){
          terr_pull = sels[r];
      }else if(sels[r].name == 'tadd_language'){
          language_pull = sels[r];
      }else if(sels[r].name == 'tadd_outlet_pull'){
          outlet_pull = sels[r];
      }else if(sels[r].name == 'tadd_deliverable_standard'){
          deliverable_standard = sels[r];
      }else if(sels[r].name == 'tadd_deliverable_frame_rate'){
          deliverable_frame_rate = sels[r];
      }else if(sels[r].name == 'tadd_deliverable_aspect_ratio'){
          deliverable_aspect_ratio = sels[r];
      }else if(sels[r].name == 'tadd_deliverable_format'){
          deliverable_format = sels[r];
      }else if(sels[r].name == 'tadd_status_triggers'){
          status_triggers = sels[r];
      }else if(sels[r].name == 'tadd_priority_triggers'){
          priority_triggers = sels[r];
      }
    }
    var start_date = '';
    var due_date = '';
    var revenue_month = '';
    var description = top_el.getElementsByClassName('tadd_description')[0];
    var deliverable_specs = top_el.getElementsByClassName('tadd_delivery_specs')[0];
    var keywords = top_el.getElementsByClassName('tadd_keywords')[0];
    var epi_val = epi_name.value
    var epis = epi_val.split(',')

    data = {'episode': epi_name.value, 'title': title.value, 'order_code': order_code,
          'description': description.value, 'keywords': keywords.value,
          'po_number': order_obj.po_number, 'order_name': order_obj.name,
          'title_id_number': title_id_num_el.value, 'priority': 100, 'audio_priority': 100,
          'compression_priority': 100, 'edeliveries_priority': 100, 'edit_priority': 100,
          'machine_room_priority': 100, 'media_vault_priority': 100, 'qc_priority': 100,
          'vault_priority': 100, 'pulled_blacks': '',
          'delivery_specs': deliverable_specs.value, 'status_triggers': status_triggers.value,
          'priority_triggers': priority_triggers.value, 'login': login}
    if(expected_price_el.value != '' && expected_price_el.value != null){
      data['expected_price'] = expected_price_el.value;
    }
    if(total_program_run_time_el.value != '' && total_program_run_time_el.value != null){
      data['total_program_runtime'] = total_program_run_time_el.value;
    }
    if(total_runtime_with_textless_el.value != '' && total_runtime_with_textless_el.value != null){
      data['total_runtime_w_textless'] = total_runtime_with_textless_el.value;
    }
    var dates = top_el.getElementsByTagName('input');
    for(var r = 0; r < dates.length; r++){
      //alert(dates[r].name);
      if(dates[r].name == 'tadd_start_date'){
          start_date = dates[r];
          //alert("START DATE: " + start_date.value);
          if(start_date.value != ''){
              data['start_date'] = start_date.value;
          }
      }else if(dates[r].name == 'tadd_due_date'){
          due_date = dates[r];
          //alert("FOUND DUE DATE: " + due_date.value);
          if(due_date.value != ''){
              data['due_date'] = due_date.value;
          }
      }else if(dates[r].name == 'tadd_rm_date'){
          revenue_month = dates[r];
          //alert("FOUND REVENUE MONTH: " + revenue_month.value);
          if(revenue_month.value != ''){
              data['expected_delivery_date'] = revenue_month.value;
          }
      }
    }
    if(client_pull != ''){
      data['client_code'] = client_pull.value.split('XsX')[0];
    }
    if(data['client_code'] == 'NOTHING'){
      data['client_code'] = ''
    }
    if(terr_pull != ''){
      data['territory'] = terr_pull.value;
    }
    if(language_pull != ''){
      data['language'] = language_pull.value;
    }
    if(outlet_pull != ''){
      if(outlet_pull.value != 'NOTHINGXsXNOTHING'){
          data['platform'] = outlet_pull.value;
      }
    }
    if(deliverable_standard != ''){
      if(deliverable_standard != 'NOTHINGXsXNOTHING'){
          data['deliverable_standard'] = deliverable_standard.value;
      }
    }
    if(deliverable_aspect_ratio != ''){
      if(deliverable_aspect_ratio != 'NOTHINGXsXNOTHING'){
          data['deliverable_aspect_ratio'] = deliverable_aspect_ratio.value;
      }
    }
    if(deliverable_format != ''){
      if(deliverable_format != 'NOTHINGXsXNOTHING'){
          data['deliverable_format'] = deliverable_format.value;
      }
    }
    if(deliverable_frame_rate != ''){
      if(deliverable_frame_rate != 'NOTHINGXsXNOTHING'){
          data['deliverable_frame_rate'] = deliverable_frame_rate.value;
      }
    }
    begin = Number(range1.value);
    end = Number(range2.value);
    new_codes = [];
    old_codes = server.eval("@GET(twog/title['order_code','" + order_code + "'].code)");
    ban_codes = [];
    for(var p = 0; p < old_codes.length; p++){
      if(!(old_codes[p] in oc(allowed_titles_arr))){
          ban_codes.push(old_codes[p]);
      }
    }
    if(pipe_pull != ''){
      proj_trans = server.eval("@SOBJECT(twog/proj_transfer['login','" + login + "'])");
      wo_trans = server.eval("@SOBJECT(twog/work_order_transfer['login','" + login + "'])");
      for(var tt = 0; tt < proj_trans.length; tt++){
          server.delete_sobject(proj_trans[tt].__search_key__);
      }
      for(var tt = 0; tt < wo_trans.length; tt++){
          server.delete_sobject(wo_trans[tt].__search_key__);
      }
      clone_actions = server.eval("@SOBJECT(twog/action_tracker['login','" + login + "']['action','cloning'])");
      for(var r = 0; r < clone_actions.length; r++){
          server.delete_sobject(clone_actions[r].__search_key__);
      }
    }
    out_epis = [];
    if(!(isNaN(begin) || isNaN(end)) && end != 0 && epis.length < 2){
      for(var r = begin; r < end + 1; r++){
          //spt.app_busy.show('Creating Title ' + title.value, ' Episode ' + r + ' of ' + begin + ' - ' + end);
          if(formatter_el.value != '' && formatter_el.value != null){
              data['episode'] = format_replace(r, '#', formatter_el.value);
              out_epis.push(format_replace(r, '#', formatter_el.value));
          }else{
              data['episode'] = r;
              out_epis.push(r);
          }
      }
    }else{
      if(epis.length > 1){
          for(var z = 0; z < epis.length; z++){
              out_epis.push(trim(epis[z]));
          }
      }else{
          out_epis.push(epi_name.value);
      }
    }
    data['pipeline_code'] = pipe_pull.value;
    spt.app_busy.show('Creating Titles');
    thing = server.execute_cmd('manual_updaters.CreateTitlesCmd', {'episodes': out_epis, 'data': data});
    // thing = server.insert('twog/title', data);
    new_codes = server.eval("@GET(twog/title['order_code','" + order_code + "'].code)");
    allowed_titles = '';
    for(var k = 0; k < new_codes.length; k++) {
        if(!(new_codes[k] in oc(ban_codes))) {
            if(allowed_titles == '') {
                allowed_titles = new_codes[k];
            } else {
                allowed_titles = allowed_titles + '|' + new_codes[k];
            }
        }
    }
    order_el.setAttribute('allowed_titles', allowed_titles);
    display_mode = order_el.getAttribute('display_mode');
    user = order_el.getAttribute('user');

    kwargs = {
               'sk': order_sk,
               'display_mode': display_mode,
               'user': user,
               'allowed_titles': allowed_titles
    };

    spt.tab.add_new('order_builder_' + order_code, 'Order Builder For ' + order_obj.name, "order_builder.order_builder.OrderBuilder", kwargs);

    spt.popup.close(spt.popup.get_popup(bvr.src_el));
    spt.app_busy.hide();
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (order_sk, order_sid, login)}
    return behavior
