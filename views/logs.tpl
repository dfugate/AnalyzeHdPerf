% include('header.tpl', title='HDPA - Logs')
% from operator import attrgetter

<h1>
    Logs
</h1>
<hr />

<div class="panel panel-primary">
    <div class="panel-heading">Server Logs</div>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Severity</th>
                <th>Time</th>
                <th>Message</th>
            </tr>
        </thead>
        <tbody>
            % for log in sorted(log_buffer, key=attrgetter('asctime'), reverse=True):
            <tr>
                <%
                 severity = "info"
                 if log.levelname == "DEBUG":
                     severity = "active"
                 elif log.levelname == "ERROR" or log.levelname == "CRITICAL":
                     severity = "danger"
                 elif log.levelname == "WARN" or log.levelname == "WARNING":
                     severity = "warning"
                 end
                %>
                <td class="{{severity}}">{{log.levelname}}</td>
                <td>{{log.asctime}}</td>
                <td>{{log.message}}</td>
            </tr>
            % end
        </tbody>
    </table>
</div>

% include('footer.tpl')