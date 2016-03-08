from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.web import Table
from pyasm.search import Search

from order_builder_utils import OBScripts


class TitleSourceInspectorWdg(BaseRefreshWdg):

    def init(my):
        my.search_type = 'twog/title'
        my.title = 'Title'
        my.sk = ''
        my.code = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>"

    def get_display(my):
        my.sk = str(my.kwargs.get('search_key'))
        my.code = my.sk.split('code=')[1]
        user_group_names = Environment.get_group_names()
        groups_str = ''
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in groups_str:
            user_is_scheduler = True
        sources_search = Search("twog/title_origin")
        sources_search.add_filter('title_code',my.code)
        sources_searched = sources_search.get_sobjects()
        sources = []
        for ss in sources_searched:
            sources.append(ss.get_value('source_code'))
        obs = OBScripts()
        table = Table()
        table.add_attr('class', 'titlesourceinspector_%s' % my.sk)
        if sources in [None,[]]:
            table.add_row()
            table.add_cell('There are no sources attached to this Title')
        else:
            for source_link in sources:
                source_search = Search("twog/source")
                source_search.add_filter('code',source_link)
                source = source_search.get_sobject()
                row = table.add_row()
                row.add_attr('class', 'titlesourceinspector_source_%s' % source.get_value('code'))
                if user_is_scheduler:
                    killer = table.add_cell(my.x_butt)
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(get_kill_title_source_behavior(source.get_value('code'),
                                                                       '%s: %s' % (source.get_value('title'),
                                                                                   source.get_value('episode')),
                                                                       my.sk))
                name = table.add_cell('<b><u>Barcode: %s  Title: %s: %s, Code : %s</u></b>' % (source.get_value('barcode'), source.get_value('title'), source.get_value('episode'), source.get_value('code')))
                name.add_attr('nowrap','nowrap')
                name.add_style('cursor: pointer;')
                name.add_behavior(obs.get_launch_source_behavior(my.code,my.sk,source.get_value('code'),source.get_search_key()))

        return table


def get_kill_title_source_behavior(source_code, source_name, title_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m43');
                      var source_code = '%s';
                      var source_name = '%s';
                      var title_sk = '%s';
                      var title_code = title_sk.split('code=')[1];
                      var order_sk = '';
                      if(confirm('Do you really want to delete ' + source_name + ' from this Title?')){
                          var server = TacticServerStub.get();
                          title_origin = server.eval("@SOBJECT(twog/title_origin['title_code','" + title_code + "']['source_code','" + source_code + "'])");
                          if(title_origin.length > 0){
                              server.delete_sobject(title_origin[0].__search_key__);
                              var title_source_els = document.getElementsByClassName('sources_' + title_sk);
                              for(var d = 0; d < title_source_els.length; d++){
                                  order_sk = title_source_els[d].getAttribute('order_sk');
                                  spt.api.load_panel(title_source_els[d], 'order_builder.SourcesRow', {title_code: title_code, title_sk: title_sk, order_sk: order_sk});
                              }
                          }
                          reload_wos = [];
                          projs = server.eval("@SOBJECT(twog/proj['title_code','" + title_code + "'])");
                          for(var r = 0; r < projs.length; r++){
                              work_orders = server.eval("@SOBJECT(twog/work_order['proj_code','" + projs[r].code + "'])");
                              for(var k = 0; k < work_orders.length; k++){
                                  wosses = server.eval("@SOBJECT(twog/work_order_sources['work_order_code','" + work_orders[k].code + "']['source_code','" + source_code + "'])");
                                  if(wosses.length > 0){
                                      reload_wos.push(work_orders[k].__search_key__);
                                  }
                                  for(var w = 0; w < wosses.length; w++){
                                      server.delete_sobject(wosses[w].__search_key__);
                                  }
                              }
                          }
                          for(var r = 0; r < reload_wos.length; r++){
                              var source_els = document.getElementsByClassName('wo_sources_' + reload_wos[r]);
                              for(var p = 0; p < source_els.length; p++){
                                  spt.api.load_panel(source_els[p], 'order_builder.WorkOrderSourcesRow', {'work_order_code': reload_wos[r].split('code=')[1], 'work_order_sk': reload_wos[r], 'order_sk': order_sk});
                              }
                          }
                         this_els = document.getElementsByClassName('titlesourceinspector_' + title_sk);
                         for(var r = 0; r < this_els.length; r++){
                             spt.api.load_panel(this_els[r], 'order_builder.TitleSourceInspectorWdg', {'search_key': title_sk});
                         }
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (source_code, source_name, title_sk)}
    return behavior
