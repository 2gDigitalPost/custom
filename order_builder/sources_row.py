from client.tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg

from order_builder_utils import get_launch_source_behavior


class SourcesRow(BaseRefreshWdg):

    def init(my):
        my.server = None
        my.title_sk = ''
        my.title_code = ''
        my.order_sk = ''

    def get_display(my):
        my.title_code = str(my.kwargs.get('title_code'))
        my.title_sk = str(my.kwargs.get('title_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))

        origin_search = Search("twog/title_origin")
        origin_search.add_filter('title_code',my.title_code)
        origins = origin_search.get_sobjects()

        groups_str = ''
        user_group_names = Environment.get_group_names()
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in groups_str:
            user_is_scheduler = True

        table = Table()
        table.add_attr('width','100%s' % '%')
        table.add_attr('bgcolor','#cbe49e')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_row()
        source_limit = 7
        count = 0
        if len(origins) > 0:
            table.add_row()
            mr_title = table.add_cell('<b><u><i>Sources</i></u></b>')
            mr_title.add_style('font-size: 90%s;' % '%')
        seen = []
        for origin in origins:
            source_code = origin.get_value('source_code')
            if source_code not in seen:
                seen.append(source_code)
                source_search = Search("twog/source")
                source_search.add_filter('code',source_code)
                source = source_search.get_sobject()
                if count % source_limit == 0:
                    table.add_row()
                celly = None
                if not source.get_value('high_security'):
                    celly = table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
                else:
                    celly = table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
                celly.add_attr('nowrap','nowrap')
                celly.add_style('cursor: pointer;')
                celly.add_style('font-size: 80%s;' % '%')
                celly.add_behavior(get_launch_source_behavior(my.title_code, my.title_sk, source.get_value('code'), source.get_search_key(), my.order_sk))

                table.add_cell(' &nbsp;&nbsp; ')
                count += 1
            else:

                my.server = TacticServerStub.get()
                my.server.retire_sobject(origin.get_search_key())
        table2 = Table()
        if user_is_scheduler:
            table2.add_row()
            barcode_text_wdg = TextWdg('barcode_insert')
            barcode_text_wdg.add_behavior(my.get_barcode_insert_behavior(my.title_code, my.title_sk, my.order_sk))
            bct = table2.add_cell(barcode_text_wdg)
            bct.add_attr('align','right')
            bct.add_attr('width','100%s' % '%')
        two_gether = Table()
        two_gether.add_row()
        srcs = two_gether.add_cell(table)
        srcs.add_attr('width','100%s' % '%')
        srcs.add_attr('valign','top')
        if user_is_scheduler:
            bcentry = two_gether.add_cell(table2)
            bcentry.add_attr('valign','top')

        return two_gether

    @staticmethod
    def get_barcode_insert_behavior(title_code, title_sk, order_sk):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                        try{
                          //alert('m39');
                          var server = TacticServerStub.get();
                          title_code = '%s';
                          title_sk = '%s';
                          order_sk = '%s';
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                          var source_el = top_el.getElementsByClassName('sources_' + title_sk)[0];
                          barcode = bvr.src_el.value;
                          barcode = barcode.toUpperCase();
                          source_expr = "@SOBJECT(twog/source['barcode','" + barcode + "'])";
                          sources = server.eval(source_expr);
                          if(sources.length > 1){
                              alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that barcode.');
                              bvr.src_el.value = '';
                          }else if(sources.length == 0){
                              source_expr = "@SOBJECT(twog/source['client_asset_id','" + barcode + "'])";
                              sources = server.eval(source_expr);
                              if(sources.length > 1){
                                  alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that client_asset_id.');
                                  bvr.src_el.value = '';
                                  sources = []
                              }
                          }
                          if(sources.length > 0){
                              source = sources[0];
                              server.insert('twog/title_origin', {title_code: title_code, source_code: source.code});
                              spt.api.load_panel(source_el, 'order_builder.SourcesRow', {title_code: title_code, title_sk: title_sk, order_sk: order_sk});
                          }else{
                              alert('There are no sources with that barcode. Try a different barcode?');
                              bvr.src_el.value = '';
                          }


                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (title_code, title_sk, order_sk)}
        return behavior