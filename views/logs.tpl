% include('header.tpl', title='HDPA - Logs')



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
            % for log in log_buffer:
            <tr>
                % severity = "info" # TODO - fix me
                <td class="{{severity}}">{{log.levelname}}</td>
                <td>{{log.asctime}}</td>
                <td>{{log.message}}</td>
            </tr>
            % end
        </tbody>
    </table>
</div>

% include('footer.tpl')