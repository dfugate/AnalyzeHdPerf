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

% if server.stopped is not None:
%   include('stats.tpl', server=server)
%   include('config.tpl', server=server)
% else:
    <div class="row">
        <div class="col-md-offset-3 col-md-6">
        <img src="/static/img/coming-soon.jpg"
             class="img-responsive"></img>
        </div>
    </div>
    <br /><br />
    <div class="well">
        The run you started at {{server.started.isoformat()}} has not yet completed. Please wait a bit and reload this
        page <b>or</b> you can also get the real-time status of this run <a href="/status">here</a>. Thanks for your
        patience.
    </div>
% end


% include('footer.tpl')