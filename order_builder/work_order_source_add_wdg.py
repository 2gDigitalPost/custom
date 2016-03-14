from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table


class WorkOrderSourceAddWdg(BaseRefreshWdg):

    def init(my):
        my.server = TacticServerStub.get()
        my.work_order_sk = ''
        my.work_order_code = ''
        my.title_code = ''
        my.order_sk = ''

    def get_snapshot_file(my, snapshot_code):
        rel_paths = my.server.get_all_paths_from_snapshot(snapshot_code, mode='relative')
        file_only = ''
        if len(rel_paths) > 0:
            rel_path = rel_paths[0]
            splits = rel_path.split('/')
            if len(splits) < 2:
                splits = rel_path.split('\\')
            file_only = splits[len(splits) - 1]
        return file_only

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.title_code = str(my.kwargs.get('title_code'))
        my.call_me = str(my.kwargs.get('call_me'))
        my.order_sk = str(my.kwargs.get('order_sk'))

        src_search = Search("twog/title_origin")
        src_search.add_filter('title_code',my.title_code)
        title_sources = src_search.get_sobjects()
        table = Table()
        table.add_attr('class', 'wo_src_attacher')
        wsrc_search = Search("twog/work_order_sources")
        wsrc_search.add_filter('work_order_code',my.work_order_code)
        wo_sources = wsrc_search.get_sobjects()
        existing = {}
        wos_lookup = {}
        for wos in wo_sources:
            wosoc = wos.get_value('source_code')
            wosnc = wos.get_value('snapshot_code')
            if wosoc not in existing.keys():
                existing[wosoc] = []
            existing[wosoc].append(wosnc)
            wos_lookup['%s%s%s' % (my.work_order_code, wosoc, wosnc)] = wos.get_search_key()
        for src in title_sources:
            src_code = src.get_value('source_code')
            rsrc_search = Search("twog/source")
            rsrc_search.add_filter('code',src_code)
            real_src = rsrc_search.get_sobject()
            real_id = real_src.get_value('id')
            table.add_row()
            is_checked = ''
            preselected = 'false'
            if src_code in existing.keys():
                is_checked = 'checked="true"'
                preselected = 'true'
            wos_sk = ''
            if '%s%s' % (my.work_order_code,src_code) in wos_lookup.keys():
                wos_sk = wos_lookup['%s%s' % (my.work_order_code,src_code)]
            table.add_cell('<input type="checkbox" class="src_add_checks" code="%s" src_code="%s" st="twog/source" preselected="%s" wos_sk="%s" %s/>' % (src_code,src_code,preselected,wos_sk,is_checked))
            table.add_cell('<u>%s</u>' % real_src.get_value('title'))
            snap_search = Search("sthpw/snapshot")
            snap_search.add_filter('search_type','twog/source?project=twog')
            snap_search.add_filter('search_id',real_id)
            snaps = snap_search.get_sobjects()

            inner_table = Table()
            for snap in snaps:
                file_only = my.get_snapshot_file(snap.get_value('code'))
                inner_table.add_row()
                checked = ''
                presel = 'false'
                if src_code in existing.keys():
                    if snap.get_value('code') in existing[src_code]:
                        checked = 'checked="true"'
                        presel = 'true'
                wos2_sk = ''
                if '%s%s%s' % (my.work_order_code,src_code,snap.get_value('code')) in wos_lookup.keys():
                    wos2_sk = wos_lookup['%s%s%s' % (my.work_order_code,src_code,snap.get_value('code'))]
                inner_table.add_cell('<input type="checkbox" class="src_add_checks" code="%s" src_code="%s" st="sthpw/snapshot" preselected="%s" wos_sk="%s" %s/>' % (snap.get_value('code'),src_code,presel,wos2_sk,checked))
                fo = inner_table.add_cell(file_only)
                fo.add_attr('nowrap','nowrap')
            table.add_row()
            table.add_cell(' ')
            table.add_cell(inner_table)
            table.add_row()
        save_tbl = Table()
        noth_1 = save_tbl.add_cell(' ')
        noth_1.add_attr('width', '100%')
        save_line = save_tbl.add_cell('<input type="button" value="Commit Changes"/>')
        save_line.add_attr('align', 'center')
        save_line.add_style('cursor: pointer;')
        save_line.add_behavior(get_attach_sources_to_wo_behavior(my.work_order_code, my.work_order_sk, my.call_me,
                                                                 my.order_sk))
        noth_2 = save_tbl.add_cell(' ')
        noth_2.add_attr('width', '100%')
        dbl = table.add_cell(save_tbl)
        dbl.add_attr('colspan', '2')

        return table


def get_attach_sources_to_wo_behavior(work_order_code, work_order_sk, call_me, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      work_order_sk = '%s';
                      call_me = '%s';
                      order_sk = '%s';
                      var top_el = spt.api.get_parent(bvr.src_el, '.wo_src_attacher');
                      all_checks = top_el.getElementsByClassName('src_add_checks');
                      code_trans = {'twog/source': 'source_code', 'sthpw/snapshot': 'snapshot_code'};
                      for(var r =0; r < all_checks.length; r++){
                          check = all_checks[r];
                          data = {'work_order_code': work_order_code};
                          if(check.getAttribute('preselected') == 'true'){
                              if(check.checked){
                                  //Do nothing, it's already been inserted
                              }else{
                                 //remove the work_order_sources entry
                                 wos_sk = check.getAttribute('wos_sk');
                                 if(wos_sk != ''){
                                     server.retire_sobject(wos_sk);
                                 }
                              }
                          }else{
                              if(check.checked){
                                  data['source_code'] = check.getAttribute('src_code')
                                  data[code_trans[check.get('st')]] = check.getAttribute('code');
                                  server.insert('twog/work_order_sources',data);
                              }else{
                                  //Do nothing, it isn't checked
                              }
                          }
                      }
                      var boss_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var sources_el = boss_el.getElementsByClassName('sources_' + work_order_sk)[0];
                      spt.api.load_panel(sources_el, 'order_builder.WorkOrderSourcesRow', {work_order_code: work_order_code, work_order_sk: work_order_sk, order_sk: order_sk});
                      spt.popup.close(spt.popup.get_popup(bvr.src_el));
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_sk, call_me, order_sk)}
    return behavior
