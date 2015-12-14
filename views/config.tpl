<div class="row">
    <div class="col-md-6">
        <div class="panel panel-primary">
            <div class="panel-heading">
                Server Configuration
            </div>
            <ul class="list-group">
                <li class="list-group-item">
                    <span class="badge">{{len(server.client_hostnames)}}</span>
                    Number of Clients
                </li>
                <li class="list-group-item">
                    <span class="badge">{{server.benchmark_time}}</span>
                    Benchmark Duration (seconds)
                </li>
                <li class="list-group-item">
                    <span class="badge">{{server.chunk_size}}</span>
                    Minimum File Chunk Size (MB)
                </li>
                <li class="list-group-item">
                    <span class="badge">{{server.file_size}}</span>
                    File Size (MB)
                </li>
                <li class="list-group-item">
                    <span class="badge">{{server.heartbeat_interval}}</span>
                    Client Ping Time (seconds)
                </li>
                <li class="list-group-item">
                    <span class="badge">{{server.monitoring_interval}}</span>
                    Client Resource Monitoring Interval (seconds)
                </li>
            </ul>
        </div>
    </div>
    <div class="col-md-6">
        <dl class="dl-horizontal">
        % if not (server.started is None):
            <dt>
                Server Started
            </dt>
            <dd>
                <span class="label label-success">{{server.started.isoformat()}}</span>
            </dd>
        % end
        % if not (server.stopped is None):
            <dt>
                Server Halted
            </dt>
            <dd>
                <span class="label label-danger">{{server.stopped.isoformat()}}</span>
            </dd>
        % end
        </dl>
    </div>
</div>