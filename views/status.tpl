% include('header.tpl', title='HDPA - Status')

<h1>
    Status
</h1>
<hr />

% benchmarks_done = len(finished) + len(failed)
% percent_complete = int(float(benchmarks_done) / float(benchmarks_done + len(running)) * 100)
% if len(failed) > 0:
%   progress_state = "progress-bar-danger"
% elif percent_complete != 100:
%   progress_state = "progress-bar-info"
% else:
%   progress_state = "progress-bar-success"
% end

<h4>Overall Progress</h4>
<div class="progress">
  <div class="progress-bar {{progress_state}}" role="progressbar"
       aria-valuenow="{{percent_complete}}" aria-valuemin="0" aria-valuemax="100"
       style="min-width: 2em; width: {{percent_complete}}%;">
    {{percent_complete}}%
  </div>
</div>

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
