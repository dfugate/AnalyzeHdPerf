% from operator import attrgetter

<div class="panel panel-primary">
    <div class="panel-heading">Client Statistics</div>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Host</th>
                <th>Chunk Size</th>
                <th>Rollover Avg.</th>
                <th>Rollover Std. Dev.</th>
                <th>Rollover Variance</th>
                <th>CPU Avg.</th>
                <th>CPU Std. Dev.</th>
                <th>CPU Variance</th>
                <th>Memory Avg.</th>
                <th>Memory Std. Dev.</th>
                <th>Memory Variance</th>
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
                <td>{{ci_stats['mem_usage_mean']}}</td>
                <td>{{ci_stats['mem_usage_stdev']}}</td>
                <td>{{ci_stats['mem_usage_variance']}}</td>
                <td class="{{status}}">{{state}}</td>
            </tr>
            % end
        </tbody>
    </table>
</div>