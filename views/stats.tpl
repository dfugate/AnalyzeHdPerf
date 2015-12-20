% from operator import attrgetter

<div class="panel panel-primary">
    <div class="panel-heading">Client Statistics</div>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th><abbr title="Client running the benchmark.">Host</abbr></th>
                <th><abbr title="MB's written to a file at a time.">Chunk Size</abbr></th>
                <th><abbr title="Average time (seconds) it took to write a single file.">Rollover Avg.</abbr></th>
                <th><abbr title="Standard deviation (seconds) for writing a single file.">Rollover Std. Dev.</abbr></th>
                <th><abbr title="Statistical variance (seconds) for writing a single file.">Rollover Variance</abbr></th>
                <th><abbr title="Average *additional* CPU usage (percent) while running the benchmark.">CPU Avg.</abbr></th>
                <th><abbr title="Standard deviation (percent) for writing all files.">CPU Std. Dev.</abbr></th>
                <th><abbr title="Statistical variance (percent) for writing all files.">CPU Variance</abbr></th>
                <th><abbr title="Memory consumption (MB) prior to running the benchmark.">Initial Memory</abbr></th>
                <th><abbr title="Average memory consumption (MB) while running the benchmark.">Memory Avg.</abbr></th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            % for ci in sorted(server.client_info_dict.values(), key=attrgetter('chunk_size')):
            <tr>
                <%
                 ci_stats = ci.get_statistics()

                 if not ci.done:
                     status = "active"
                     state = "Pending"
                 elif ci.stopped is None:
                     status = "danger"
                     state = "Failed"
                 else:
                     status = "success"
                     state = "Complete"
                 end
                %>
                <td>{{ci.hostname}}</td>
                <td>{{ci.chunk_size}}</td>
                <td>{{ci_stats['rollover_mean']}}</td>
                <td>{{ci_stats['rollover_stdev']}}</td>
                <td>{{ci_stats['rollover_variance']}}</td>
                <td>{{ci_stats['cpu_util_mean']}}</td>
                <td>{{ci_stats['cpu_util_stdev']}}</td>
                <td>{{ci_stats['cpu_util_variance']}}</td>
                <td>{{ci_stats['initial_mem_usage']}}</td>
                <td>{{ci_stats['mem_usage_mean']}}</td>
                <td class="{{status}}">{{state}}</td>
            </tr>
            % end
        </tbody>
    </table>
</div>