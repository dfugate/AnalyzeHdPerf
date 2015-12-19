% include('header.tpl', title='HDPA - About')

<h1>
    About
</h1>
<hr />

<div class="well">
    <p>
    <i>Hard Drive Performance Analyzer</i> is open source and the full source code is available on my
    <a onclick="window.open('https://github.com/dfugate/AnalyzeHdPerf'); return false;" style="cursor: pointer;">
    GitHub account</a>.
    </p>

    <h4>Key Features</h4>
    <ul>
        <li>Server/client configuration parameters are settable from the command-prompt.</li>
        <li>Clients run file-creation tasks for a designated amount of time and then shutdown.</li>
        <li>Server owns instantiation of test clients and kicks them off via SSH. Also, the server is capable of
            handling multiple concurrent clients running either locally or remotely.</li>
        <li>Clients communicate performance data (e.g., file rollover time, total CPU utilization, and
            memory consumption) to the server via RESTful services. Clients are expected to send so-called
            “heartbeat” notifications at designated intervals.</li>
        <li>A server thread monitors the health of it’s clients through these heartbeats and “knows” when they’ve died
            suddenly.</li>
        <li>Virtually everything is logged – server and client. Clients send (most) of their logs to the server which
            are then rendered on the <a href="/logs">“Logs”</a> page.</li>
    </ul>

    <h4>Technologies</h4>
    <ul>
        <li>Server and client are powered by Python 2.7</li>
        <li>Tested against both Ubuntu and Mac OS</li>
        <li>Server’s web front-end uses the lightweight <i>bottle</i>  framework in conjunction with
            Bootstrap.
        </li>
        <li>A port of Python 3.4’s <i>statistics</i> module is utilized in lieu of <i>NumPy</i> which would have been
            overkill for my purposes.</li>
        <li>I really wanted to do something
            <a onclick="window.open('http://projects.flowingdata.com/life-expectancy');return false;" style="cursor: pointer;">
            cool with D3.js</a> in terms of the <a href="/report">Report</a>.
            This is quite time consuming though, and I thought it was more important to take my four and six-year old
            sons to the new Star Wars flick with my limited free time&#x1F600;
        </li>
        <li>Clients use Google’s <i>psutil</i> package to glean performance data.
        <li>Look over the
            <a onclick="window.open('https://github.com/dfugate/AnalyzeHdPerf'); return false;" style="cursor: pointer;">
            Sources</a> for any other cool techs I may have forgotten to mention.
        </li>
    </ul>

</div>

% include('footer.tpl')