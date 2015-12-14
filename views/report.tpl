% include('header.tpl', title='HDPA - Report')

<script src="/static/js/d3.min.js"></script>
<script>
    "use strict";
    var data = [
        % for ci in server.client_info_dict.values():
        {{!ci.to_json()}},
        % end
    ];
</script>
<script src="/static/js/report.js"></script>

<h1>
    Report
</h1>
<hr />

<p class="bg-primary">
    Not much to see yet!
</p>

% include('config.tpl', server=server)

% include('footer.tpl')