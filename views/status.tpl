% include('header.tpl', title='HDPA - Status')

<h1>
    Status
</h1>
<hr />

<div class="panel panel-primary">
    <div class="panel-heading">Client Status</div>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Host</th>
                <th>Chunk Size</th>
                <th>Last Checked</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            % for ci in running:
            <tr>
                <td>{{ci.hostname}}</td>
                <td>{{ci.chunk_size}}</td>
                <td>{{ci.get_last_contact()}}</td>
                <td class="active">Pending</td>
            </tr>
            % end
            % for ci in finished:
            <tr>
                <td>{{ci.hostname}}</td>
                <td>{{ci.chunk_size}}</td>
                <td>{{ci.get_last_contact()}}</td>
                <td class="success">Complete</td>
            </tr>
            % end
            % for ci in failed:
            <tr>
                <td>{{ci.hostname}}</td>
                <td>{{ci.chunk_size}}</td>
                <td>{{ci.get_last_contact()}}</td>
                <td class="danger">Failed</td>
            </tr>
            % end
        </tbody>
    </table>
</div>

% include('config.tpl', server=server)

% include('footer.tpl')
