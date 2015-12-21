from tactic_client_lib import TacticServerStub


server = TacticServerStub.get(protocol="xmlrpc")

new_sobjects = [
    {
        'type': 'twog/action_tracker',
        'name': 'Predetermined twog/action_tracker',
        'description':
            'Predetermined Asset for holding uploads to any twog/action_tracker that has not been created yet'
    },
    {
        'type': 'twog/archived_files',
        'name': 'Predetermined twog/archived_files',
        'description':
            'Predetermined Asset for holding uploads to any twog/archived_files that has not been created yet'
    },
    {
        'type': 'twog/asset_to_movement',
        'name': 'Predetermined twog/asset_to_movement',
        'description':
            'Predetermined Asset for holding uploads to any twog/asset_to_movement that has not been created yet'
    },
    {
        'type': 'twog/barcode',
        'name': 'Predetermined twog/barcode',
        'description':
            'Predetermined Asset for holding uploads to any twog/barcode that has not been created yet'
    },
    {
        'type': 'twog/bundled_message',
        'name': 'Predetermined twog/bundled_message',
        'description':
            'Predetermined Asset for holding uploads to any twog/bundled_message that has not been created yet'
    },
    {
        'type': 'twog/client',
        'name': 'Predetermined twog/client',
        'description':
            'Predetermined Asset for holding uploads to any twog/client that has not been created yet'
    },
    {
        'type': 'twog/client_pipes',
        'name': 'Predetermined twog/client_pipes',
        'description':
            'Predetermined Asset for holding uploads to any twog/client_pipes that has not been created yet'
    },
    {
        'type': 'twog/combo_pipe',
        'name': 'Predetermined twog/combo_pipe',
        'description':
            'Predetermined Asset for holding uploads to any twog/combo_pipe that has not been created yet'
    },
    {
        'type': 'twog/company',
        'name': 'Predetermined twog/company',
        'description':
            'Predetermined Asset for holding uploads to any twog/company that has not been created yet'
    },
    {
        'type': 'twog/custom_property',
        'name': 'Predetermined twog/custom_property',
        'description':
            'Predetermined Asset for holding uploads to any twog/custom_property that has not been created yet'
    },
    {
        'type': 'twog/custom_script',
        'name': 'Predetermined twog/custom_script',
        'description':
            'Predetermined Asset for holding uploads to any twog/custom_script that has not been created yet'
    },
    {
        'type': 'twog/deliverable',
        'name': 'Predetermined twog/deliverable',
        'description':
            'Predetermined Asset for holding uploads to any twog/deliverable that has not been created yet'
    },
    {
        'type': 'twog/deliverable_spec',
        'name': 'Predetermined twog/deliverable_spec',
        'description':
            'Predetermined Asset for holding uploads to any twog/deliverable_spec that has not been created yet'
    },
    {
        'type': 'twog/deliverable_templ',
        'name': 'Predetermined twog/deliverable_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/deliverable_templ that has not been created yet'
    },
    {
        'type': 'twog/element_eval',
        'name': 'Predetermined twog/element_eval',
        'description':
            'Predetermined Asset for holding uploads to any twog/element_eval that has not been created yet'
    },
    {
        'type': 'twog/element_eval_audio',
        'name': 'Predetermined twog/element_eval_audio',
        'description':
            'Predetermined Asset for holding uploads to any twog/element_eval_audio that has not been created yet'
    },
    {
        'type': 'twog/element_eval_barcodes',
        'name': 'Predetermined twog/element_eval_barcodes',
        'description':
            'Predetermined Asset for holding uploads to any twog/element_eval_barcodes that has not been created yet'
    },
    {
        'type': 'twog/element_eval_lines',
        'name': 'Predetermined twog/element_eval_lines',
        'description':
            'Predetermined Asset for holding uploads to any twog/element_eval_lines that has not been created yet'
    },
    {
        'type': 'twog/equipment',
        'name': 'Predetermined twog/equipment',
        'description':
            'Predetermined Asset for holding uploads to any twog/equipment that has not been created yet'
    },
    {
        'type': 'twog/equipment_unit_cost',
        'name': 'Predetermined twog/equipment_unit_cost',
        'description':
            'Predetermined Asset for holding uploads to any twog/equipment_unit_cost that has not been created yet'
    },
    {
        'type': 'twog/equipment_used',
        'name': 'Predetermined twog/equipment_used',
        'description':
            'Predetermined Asset for holding uploads to any twog/equipment_used that has not been created yet'
    },
    {
        'type': 'twog/equipment_used_templ',
        'name': 'Predetermined twog/equipment_used_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/equipment_used_templ that has not been created yet'
    },
    {
        'type': 'twog/error_report',
        'name': 'Predetermined twog/error_report',
        'description':
            'Predetermined Asset for holding uploads to any twog/error_report that has not been created yet'
    },
    {
        'type': 'twog/global_resource',
        'name': 'Predetermined twog/global_resource',
        'description':
            'Predetermined Asset for holding uploads to any twog/global_resource that has not been created yet'
    },
    {
        'type': 'twog/hackpipe_in',
        'name': 'Predetermined twog/hackpipe_in',
        'description':
            'Predetermined Asset for holding uploads to any twog/hackpipe_in that has not been created yet'
    },
    {
        'type': 'twog/hackpipe_out',
        'name': 'Predetermined twog/hackpipe_out',
        'description':
            'Predetermined Asset for holding uploads to any twog/hackpipe_out that has not been created yet'
    },
    {
        'type': 'twog/intermediate_file',
        'name': 'Predetermined twog/intermediate_file',
        'description':
            'Predetermined Asset for holding uploads to any twog/intermediate_file that has not been created yet'
    },
    {
        'type': 'twog/intermediate_file_templ',
        'name': 'Predetermined twog/intermediate_file_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/intermediate_file_templ that has not been created yet'
    },
    {
        'type': 'twog/language',
        'name': 'Predetermined twog/language',
        'description':
            'Predetermined Asset for holding uploads to any twog/language that has not been created yet'
    },
    {
        'type': 'twog/metadata_report',
        'name': 'Predetermined twog/metadata_report',
        'description':
            'Predetermined Asset for holding uploads to any twog/metadata_report that has not been created yet'
    },
    {
        'type': 'twog/movement',
        'name': 'Predetermined twog/movement',
        'description':
            'Predetermined Asset for holding uploads to any twog/movement that has not been created yet'
    },
    {
        'type': 'twog/naming',
        'name': 'Predetermined twog/naming',
        'description':
            'Predetermined Asset for holding uploads to any twog/naming that has not been created yet'
    },
    {
        'type': 'twog/order',
        'name': 'Predetermined twog/order',
        'description':
            'Predetermined Asset for holding uploads to any twog/order that has not been created yet'
    },
    {
        'type': 'twog/order_report',
        'name': 'Predetermined twog/order_report',
        'description':
            'Predetermined Asset for holding uploads to any twog/order_report that has not been created yet'
    },
    {
        'type': 'twog/outside_barcode',
        'name': 'Predetermined twog/outside_barcode',
        'description':
            'Predetermined Asset for holding uploads to any twog/outside_barcode that has not been created yet'
    },
    {
        'type': 'twog/payment',
        'name': 'Predetermined twog/payment',
        'description':
            'Predetermined Asset for holding uploads to any twog/payment that has not been created yet'
    },
    {
        'type': 'twog/person',
        'name': 'Predetermined twog/person',
        'description':
            'Predetermined Asset for holding uploads to any twog/person that has not been created yet'
    },
    {
        'type': 'twog/pipeline_prereq',
        'name': 'Predetermined twog/pipeline_prereq',
        'description':
            'Predetermined Asset for holding uploads to any twog/pipeline_prereq that has not been created yet'
    },
    {
        'type': 'twog/platform',
        'name': 'Predetermined twog/platform',
        'description':
            'Predetermined Asset for holding uploads to any twog/platform that has not been created yet'
    },
    {
        'type': 'twog/prequal_eval',
        'name': 'Predetermined twog/prequal_eval',
        'description':
            'Predetermined Asset for holding uploads to any twog/prequal_eval that has not been created yet'
    },
    {
        'type': 'twog/prequal_eval_lines',
        'name': 'Predetermined twog/prequal_eval_lines',
        'description':
            'Predetermined Asset for holding uploads to any twog/prequal_eval_lines that has not been created yet'
    },
    {
        'type': 'twog/priority_log',
        'name': 'Predetermined twog/priority_log',
        'description':
            'Predetermined Asset for holding uploads to any twog/priority_log that has not been created yet'
    },
    {
        'type': 'twog/prod_setting',
        'name': 'Predetermined twog/prod_setting',
        'description':
            'Predetermined Asset for holding uploads to any twog/prod_setting that has not been created yet'
    },
    {
        'type': 'twog/production_error',
        'name': 'Predetermined twog/production_error',
        'description':
            'Predetermined Asset for holding uploads to any twog/production_error that has not been created yet'
    },
    {
        'type': 'twog/proj',
        'name': 'Predetermined twog/proj',
        'description':
            'Predetermined Asset for holding uploads to any twog/proj that has not been created yet'
    },
    {
        'type': 'twog/proj_pricing',
        'name': 'Predetermined twog/proj_pricing',
        'description':
            'Predetermined Asset for holding uploads to any twog/proj_pricing that has not been created yet'
    },
    {
        'type': 'twog/proj_templ',
        'name': 'Predetermined twog/proj_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/proj_templ that has not been created yet'
    },
    {
        'type': 'twog/proj_transfer',
        'name': 'Predetermined twog/proj_transfer',
        'description':
            'Predetermined Asset for holding uploads to any twog/proj_transfer that has not been created yet'
    },
    {
        'type': 'twog/proj_translation',
        'name': 'Predetermined twog/proj_translation',
        'description':
            'Predetermined Asset for holding uploads to any twog/proj_translation that has not been created yet'
    },
    {
        'type': 'twog/qc_report_vars',
        'name': 'Predetermined twog/qc_report_vars',
        'description':
            'Predetermined Asset for holding uploads to any twog/qc_report_vars that has not been created yet'
    },
    {
        'type': 'twog/rate_card',
        'name': 'Predetermined twog/rate_card',
        'description':
            'Predetermined Asset for holding uploads to any twog/rate_card that has not been created yet'
    },
    {
        'type': 'twog/rate_card_item',
        'name': 'Predetermined twog/rate_card_item',
        'description':
            'Predetermined Asset for holding uploads to any twog/rate_card_item that has not been created yet'
    },
    {
        'type': 'twog/report_day',
        'name': 'Predetermined twog/report_day',
        'description':
            'Predetermined Asset for holding uploads to any twog/report_day that has not been created yet'
    },
    {
        'type': 'twog/shipper',
        'name': 'Predetermined twog/shipper',
        'description':
            'Predetermined Asset for holding uploads to any twog/shipper that has not been created yet'
    },
    {
        'type': 'twog/source',
        'name': 'Predetermined twog/source',
        'description':
            'Predetermined Asset for holding uploads to any twog/source that has not been created yet'
    },
    {
        'type': 'twog/source_issues',
        'name': 'Predetermined twog/source_issues',
        'description':
            'Predetermined Asset for holding uploads to any twog/source_issues that has not been created yet'
    },
    {
        'type': 'twog/source_log',
        'name': 'Predetermined twog/source_log',
        'description':
            'Predetermined Asset for holding uploads to any twog/source_log that has not been created yet'
    },
    {
        'type': 'twog/source_req',
        'name': 'Predetermined twog/source_req',
        'description':
            'Predetermined Asset for holding uploads to any twog/source_req that has not been created yet'
    },
    {
        'type': 'twog/spt_client_trigger',
        'name': 'Predetermined twog/spt_client_trigger',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_client_trigger that has not been created yet'
    },
    {
        'type': 'twog/spt_ingest_rule',
        'name': 'Predetermined twog/spt_ingest_rule',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_ingest_rule that has not been created yet'
    },
    {
        'type': 'twog/spt_ingest_session',
        'name': 'Predetermined twog/spt_ingest_session',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_ingest_session that has not been created yet'
    },
    {
        'type': 'twog/spt_plugin',
        'name': 'Predetermined twog/spt_plugin',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_plugin that has not been created yet'
    },
    {
        'type': 'twog/spt_process',
        'name': 'Predetermined twog/spt_process',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_process that has not been created yet'
    },
    {
        'type': 'twog/spt_trigger',
        'name': 'Predetermined twog/spt_trigger',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_trigger that has not been created yet'
    },
    {
        'type': 'twog/spt_url',
        'name': 'Predetermined twog/spt_url',
        'description':
            'Predetermined Asset for holding uploads to any twog/spt_url that has not been created yet'
    },
    {
        'type': 'twog/status_log',
        'name': 'Predetermined twog/status_log',
        'description':
            'Predetermined Asset for holding uploads to any twog/status_log that has not been created yet'
    },
    {
        'type': 'twog/tech_eval',
        'name': 'Predetermined twog/tech_eval',
        'description':
            'Predetermined Asset for holding uploads to any twog/tech_eval that has not been created yet'
    },
    {
        'type': 'twog/title',
        'name': 'Predetermined twog/title',
        'description':
            'Predetermined Asset for holding uploads to any twog/title that has not been created yet'
    },
    {
        'type': 'twog/title_origin',
        'name': 'Predetermined twog/title_origin',
        'description':
            'Predetermined Asset for holding uploads to any twog/title_origin that has not been created yet'
    },
    {
        'type': 'twog/title_prereq',
        'name': 'Predetermined twog/title_prereq',
        'description':
            'Predetermined Asset for holding uploads to any twog/title_prereq that has not been created yet'
    },
    {
        'type': 'twog/title_templ',
        'name': 'Predetermined twog/title_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/title_templ that has not been created yet'
    },
    {
        'type': 'twog/whats_new',
        'name': 'Predetermined twog/whats_new',
        'description':
            'Predetermined Asset for holding uploads to any twog/whats_new that has not been created yet'
    },
    {
        'type': 'twog/widget_config',
        'name': 'Predetermined twog/widget_config',
        'description':
            'Predetermined Asset for holding uploads to any twog/widget_config that has not been created yet'
    },
    {
        'type': 'twog/wo_instruction_changes',
        'name': 'Predetermined twog/wo_instruction_changes',
        'description':
            'Predetermined Asset for holding uploads to any twog/wo_instruction_changes that has not been created yet'
    },
    {
        'type': 'twog/wo_report',
        'name': 'Predetermined twog/wo_report',
        'description':
            'Predetermined Asset for holding uploads to any twog/wo_report that has not been created yet'
    },
    {
        'type': 'twog/work_order',
        'name': 'Predetermined twog/work_order',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order that has not been created yet'
    },
    {
        'type': 'twog/work_order_deliverables',
        'name': 'Predetermined twog/work_order_deliverables',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_deliverables that has not been created yet'
    },
    {
        'type': 'twog/work_order_intermediate',
        'name': 'Predetermined twog/work_order_intermediate',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_intermediate that has not been created yet'
    },
    {
        'type': 'twog/work_order_passin',
        'name': 'Predetermined twog/work_order_passin',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_passin that has not been created yet'
    },
    {
        'type': 'twog/work_order_passin_templ',
        'name': 'Predetermined twog/work_order_passin_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_passin_templ that has not been created yet'
    },
    {
        'type': 'twog/work_order_prereq',
        'name': 'Predetermined twog/work_order_prereq',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_prereq that has not been created yet'
    },
    {
        'type': 'twog/work_order_prereq_templ',
        'name': 'Predetermined twog/work_order_prereq_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_prereq_templ that has not been created yet'
    },
    {
        'type': 'twog/work_order_sources',
        'name': 'Predetermined twog/work_order_sources',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_sources that has not been created yet'
    },
    {
        'type': 'twog/work_order_templ',
        'name': 'Predetermined twog/work_order_templ',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_templ that has not been created yet'
    },
    {
        'type': 'twog/work_order_transfer',
        'name': 'Predetermined twog/work_order_transfer',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_transfer that has not been created yet'
    },
    {
        'type': 'twog/work_order_translation',
        'name': 'Predetermined twog/work_order_translation',
        'description':
            'Predetermined Asset for holding uploads to any twog/work_order_translation that has not been created yet'
    },
    {
        'type': 'sthpw/access_log',
        'name': 'Predetermined sthpw/access_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/access_log that has not been created yet'
    },
    {
        'type': 'sthpw/access_rule',
        'name': 'Predetermined sthpw/access_rule',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/access_rule that has not been created yet'
    },
    {
        'type': 'sthpw/access_rule_in_group',
        'name': 'Predetermined sthpw/access_rule_in_group',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/access_rule_in_group that has not been created yet'
    },
    {
        'type': 'sthpw/annotation',
        'name': 'Predetermined sthpw/annotation',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/annotation that has not been created yet'
    },
    {
        'type': 'sthpw/cache',
        'name': 'Predetermined sthpw/cache',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/cache that has not been created yet'
    },
    {
        'type': 'sthpw/clipboard',
        'name': 'Predetermined sthpw/clipboard',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/clipboard that has not been created yet'
    },
    {
        'type': 'sthpw/command',
        'name': 'Predetermined sthpw/command',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/command that has not been created yet'
    },
    {
        'type': 'sthpw/command_log',
        'name': 'Predetermined sthpw/command_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/command_log that has not been created yet'
    },
    {
        'type': 'sthpw/connection',
        'name': 'Predetermined sthpw/connection',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/connection that has not been created yet'
    },
    {
        'type': 'sthpw/custom_property',
        'name': 'Predetermined sthpw/custom_property',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/custom_property that has not been created yet'
    },
    {
        'type': 'sthpw/custom_script',
        'name': 'Predetermined sthpw/custom_script',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/custom_script that has not been created yet'
    },
    {
        'type': 'sthpw/db_resource',
        'name': 'Predetermined sthpw/db_resource',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/db_resource that has not been created yet'
    },
    {
        'type': 'sthpw/debug_log',
        'name': 'Predetermined sthpw/debug_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/debug_log that has not been created yet'
    },
    {
        'type': 'sthpw/doc',
        'name': 'Predetermined sthpw/doc',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/doc that has not been created yet'
    },
    {
        'type': 'sthpw/exception_log',
        'name': 'Predetermined sthpw/exception_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/exception_log that has not been created yet'
    },
    {
        'type': 'sthpw/file',
        'name': 'Predetermined sthpw/file',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/file that has not been created yet'
    },
    {
        'type': 'sthpw/file_access',
        'name': 'Predetermined sthpw/file_access',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/file_access that has not been created yet'
    },
    {
        'type': 'sthpw/group_notification',
        'name': 'Predetermined sthpw/group_notification',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/group_notification that has not been created yet'
    },
    {
        'type': 'sthpw/login',
        'name': 'Predetermined sthpw/login',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/login that has not been created yet'
    },
    {
        'type': 'sthpw/login_group',
        'name': 'Predetermined sthpw/login_group',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/login_group that has not been created yet'
    },
    {
        'type': 'sthpw/login_in_group',
        'name': 'Predetermined sthpw/login_in_group',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/login_in_group that has not been created yet'
    },
    {
        'type': 'sthpw/milestone',
        'name': 'Predetermined sthpw/milestone',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/milestone that has not been created yet'
    },
    {
        'type': 'sthpw/naming',
        'name': 'Predetermined sthpw/naming',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/naming that has not been created yet'
    },
    {
        'type': 'sthpw/note',
        'name': 'Predetermined sthpw/note',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/note that has not been created yet'
    },
    {
        'type': 'sthpw/notification',
        'name': 'Predetermined sthpw/notification',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/notification that has not been created yet'
    },
    {
        'type': 'sthpw/notification_log',
        'name': 'Predetermined sthpw/notification_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/notification_log that has not been created yet'
    },
    {
        'type': 'sthpw/notification_login',
        'name': 'Predetermined sthpw/notification_login',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/notification_login that has not been created yet'
    },
    {
        'type': 'sthpw/pg_ts_cfg',
        'name': 'Predetermined sthpw/pg_ts_cfg',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pg_ts_cfg that has not been created yet'
    },
    {
        'type': 'sthpw/pg_ts_cfgmap',
        'name': 'Predetermined sthpw/pg_ts_cfgmap',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pg_ts_cfgmap that has not been created yet'
    },
    {
        'type': 'sthpw/pga_diagrams',
        'name': 'Predetermined sthpw/pga_diagrams',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_diagrams that has not been created yet'
    },
    {
        'type': 'sthpw/pga_forms',
        'name': 'Predetermined sthpw/pga_forms',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_forms that has not been created yet'
    },
    {
        'type': 'sthpw/pga_graphs',
        'name': 'Predetermined sthpw/pga_graphs',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_graphs that has not been created yet'
    },
    {
        'type': 'sthpw/pga_images',
        'name': 'Predetermined sthpw/pga_images',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_images that has not been created yet'
    },
    {
        'type': 'sthpw/pga_layout',
        'name': 'Predetermined sthpw/pga_layout',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_layout that has not been created yet'
    },
    {
        'type': 'sthpw/pga_queries',
        'name': 'Predetermined sthpw/pga_queries',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_queries that has not been created yet'
    },
    {
        'type': 'sthpw/pga_reports',
        'name': 'Predetermined sthpw/pga_reports',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_reports that has not been created yet'
    },
    {
        'type': 'sthpw/pga_schema',
        'name': 'Predetermined sthpw/pga_schema',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_schema that has not been created yet'
    },
    {
        'type': 'sthpw/pga_scripts',
        'name': 'Predetermined sthpw/pga_scripts',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pga_scripts that has not been created yet'
    },
    {
        'type': 'sthpw/pipeline',
        'name': 'Predetermined sthpw/pipeline',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pipeline that has not been created yet'
    },
    {
        'type': 'sthpw/pref_list',
        'name': 'Predetermined sthpw/pref_list',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pref_list that has not been created yet'
    },
    {
        'type': 'sthpw/pref_setting',
        'name': 'Predetermined sthpw/pref_setting',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/pref_setting that has not been created yet'
    },
    {
        'type': 'sthpw/prod_setting',
        'name': 'Predetermined sthpw/prod_setting',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/prod_setting that has not been created yet'
    },
    {
        'type': 'sthpw/project',
        'name': 'Predetermined sthpw/project',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/project that has not been created yet'
    },
    {
        'type': 'sthpw/project_type',
        'name': 'Predetermined sthpw/project_type',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/project_type that has not been created yet'
    },
    {
        'type': 'sthpw/queue',
        'name': 'Predetermined sthpw/queue',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/queue that has not been created yet'
    },
    {
        'type': 'sthpw/remote_repo',
        'name': 'Predetermined sthpw/remote_repo',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/remote_repo that has not been created yet'
    },
    {
        'type': 'sthpw/repo',
        'name': 'Predetermined sthpw/repo',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/repo that has not been created yet'
    },
    {
        'type': 'sthpw/retire_log',
        'name': 'Predetermined sthpw/retire_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/retire_log that has not been created yet'
    },
    {
        'type': 'sthpw/schema',
        'name': 'Predetermined sthpw/schema',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/schema that has not been created yet'
    },
    {
        'type': 'sthpw/search_object',
        'name': 'Predetermined sthpw/search_object',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/search_object that has not been created yet'
    },
    {
        'type': 'sthpw/snapshot',
        'name': 'Predetermined sthpw/snapshot',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/snapshot that has not been created yet'
    },
    {
        'type': 'sthpw/snapshot_type',
        'name': 'Predetermined sthpw/snapshot_type',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/snapshot_type that has not been created yet'
    },
    {
        'type': 'sthpw/sobject_list',
        'name': 'Predetermined sthpw/sobject_list',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/sobject_list that has not been created yet'
    },
    {
        'type': 'sthpw/sobject_log',
        'name': 'Predetermined sthpw/sobject_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/sobject_log that has not been created yet'
    },
    {
        'type': 'sthpw/special_day',
        'name': 'Predetermined sthpw/special_day',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/special_day that has not been created yet'
    },
    {
        'type': 'sthpw/spt_client_trigger',
        'name': 'Predetermined sthpw/spt_client_trigger',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_client_trigger that has not been created yet'
    },
    {
        'type': 'sthpw/spt_ingest_rule',
        'name': 'Predetermined sthpw/spt_ingest_rule',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_ingest_rule that has not been created yet'
    },
    {
        'type': 'sthpw/spt_ingest_session',
        'name': 'Predetermined sthpw/spt_ingest_session',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_ingest_session that has not been created yet'
    },
    {
        'type': 'sthpw/spt_plugin',
        'name': 'Predetermined sthpw/spt_plugin',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_plugin that has not been created yet'
    },
    {
        'type': 'sthpw/spt_process',
        'name': 'Predetermined sthpw/spt_process',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_process that has not been created yet'
    },
    {
        'type': 'sthpw/spt_trigger',
        'name': 'Predetermined sthpw/spt_trigger',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_trigger that has not been created yet'
    },
    {
        'type': 'sthpw/spt_url',
        'name': 'Predetermined sthpw/spt_url',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/spt_url that has not been created yet'
    },
    {
        'type': 'sthpw/status_log',
        'name': 'Predetermined sthpw/status_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/status_log that has not been created yet'
    },
    {
        'type': 'sthpw/task',
        'name': 'Predetermined sthpw/task',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/task that has not been created yet'
    },
    {
        'type': 'sthpw/template',
        'name': 'Predetermined sthpw/template',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/template that has not been created yet'
    },
    {
        'type': 'sthpw/ticket',
        'name': 'Predetermined sthpw/ticket',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/ticket that has not been created yet'
    },
    {
        'type': 'sthpw/timecard',
        'name': 'Predetermined sthpw/timecard',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/timecard that has not been created yet'
    },
    {
        'type': 'sthpw/transaction_log',
        'name': 'Predetermined sthpw/transaction_log',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/transaction_log that has not been created yet'
    },
    {
        'type': 'sthpw/transaction_state',
        'name': 'Predetermined sthpw/transaction_state',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/transaction_state that has not been created yet'
    },
    {
        'type': 'sthpw/translation',
        'name': 'Predetermined sthpw/translation',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/translation that has not been created yet'
    },
    {
        'type': 'sthpw/trigger',
        'name': 'Predetermined sthpw/trigger',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/trigger that has not been created yet'
    },
    {
        'type': 'sthpw/trigger_in_command',
        'name': 'Predetermined sthpw/trigger_in_command',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/trigger_in_command that has not been created yet'
    },
    {
        'type': 'sthpw/wdg_settings',
        'name': 'Predetermined sthpw/wdg_settings',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/wdg_settings that has not been created yet'
    },
    {
        'type': 'sthpw/widget_config',
        'name': 'Predetermined sthpw/widget_config',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/widget_config that has not been created yet'
    },
    {
        'type': 'sthpw/widget_extend',
        'name': 'Predetermined sthpw/widget_extend',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/widget_extend that has not been created yet'
    },
    {
        'type': 'sthpw/work_hour',
        'name': 'Predetermined sthpw/work_hour',
        'description':
            'Predetermined Asset for holding uploads to any sthpw/work_hour that has not been created yet'
    }
]

for new_sobject in new_sobjects:
    server.insert('twog/global_resource', new_sobject)
